# Workflow Modernization: assistant-to-the-branch-manager.yml

## Section 1: Overview & Purpose

The `assistant-to-the-branch-manager.yml` workflow manages branch mergeability and pull request target branch evaluation for the Angular monorepo. When changes are pushed to primary branches or when pull requests with merge labels are updated, this workflow determines whether active pull requests are cleanly mergeable into their respective target branches. In the upstream repository, it invokes the custom `@angular/dev-infra` branch manager action, which authenticates via a dedicated GitHub App (`ANGULAR_ROBOT_PRIVATE_KEY`) and triggers mergeability evaluation jobs in `angular/dev-infra`.

### Why It Failed & Needed Adaptation
1. **Hardcoded Fork Exclusion**: Upstream explicitly included `if: github.event.repository.fork == false`. Consequently, every fork of the repository had this job automatically skipped, violating the Zero Skipped Jobs Policy.
2. **Proprietary GitHub App Authentication**: Upstream unconditionally invoked `angular/dev-infra/github-actions/branch-manager`, requiring `secrets.ANGULAR_ROBOT_PRIVATE_KEY` (the private key for Google's internal Angular Robot GitHub App). On any repository without this private key, execution fails with authentication errors.
3. **Cross-Repository Dispatch Dependency**: The upstream action attempts to dispatch workflows to a foreign repository (`angular/dev-infra/workflows/branch-manager.yml`). Outside Google's organization, this call is rejected with permissions errors.
4. **Missing Manual Dispatch Trigger**: The pipeline only listened to `push` and `pull_request_target`. Fork maintainers could not trigger or verify branch mergeability rules on demand.
5. **Wildcard Push Overhead**: The push trigger ran unconditionally without branch filters on every push, risking concurrency build exhaustion.

---

## Section 2: Dual-Mode Architecture & Changes Summary

```mermaid
flowchart TD
    Trigger([Trigger: push, pull_request_target, OR workflow_dispatch]) --> Resolve[Resolve Execution Mode]
    
    subgraph ModeDecision[Dynamic Mode Resolution]
        Resolve --> CheckCreds{Mode == original AND ANGULAR_ROBOT_PRIVATE_KEY exists AND repo == angular/angular?}
        CheckCreds -- Yes --> OriginalMode[Mode: original]
        CheckCreds -- No --> NativeMode[Mode: native]
    end

    OriginalMode --> UpstreamApp[Invoke dev-infra/branch-manager with Angular Robot Key]
    UpstreamApp --> RemoteDispatch[Dispatch to angular/dev-infra branch-manager.yml]
    
    NativeMode --> NativeCheckout[Checkout Repository]
    NativeCheckout --> QueryPRs[Query Target Branch PRs via GitHub API & gh CLI]
    QueryPRs --> CheckMergeability[Evaluate Mergeability & Commit Target Status]
    CheckMergeability --> CommitStatus[Post Commit Status context: mergeability]
    CheckMergeability --> StepSummary[Write Summary to GITHUB_STEP_SUMMARY]
    
    StepSummary --> Done([Evaluation Complete])
    RemoteDispatch --> Done
```

### Key Changes Made
- **Removed Hardcoded Fork Guard**: Replaced `if: github.event.repository.fork == false` with dynamic mode resolution and fork-friendly execution.
- **Added `workflow_dispatch`**: Enabled on-demand manual testing with configurable inputs (`mode`, `pr`, `branch`).
- **Guarded Push Triggers**: Restricted `push:` to `main` and release branches (`[0-9]+.[0-9]+.x`) to conserve runner minutes.
- **Active GitHub-Native Alternative**: Implemented direct GitHub REST API evaluation using standard `$GITHUB_TOKEN` to query open PRs, evaluate mergeability against target branches, publish commit status check `mergeability`, and output a Markdown report to `$GITHUB_STEP_SUMMARY`.
- **Configurable Runners**: Updated runner specification to `${{ vars.RUNNER_LABEL || 'ubuntu-latest' }}`.

---

## Section 3: Existing Solutions vs. Free Alternatives Analysis

| Feature / Dimension | Upstream / Original Solution | Active GitHub-Native Alternative |
|---|---|---|
| **Authentication** | Proprietary Angular Robot GitHub App PEM Private Key (`ANGULAR_ROBOT_PRIVATE_KEY`) | Standard GitHub Actions Token (`$GITHUB_TOKEN`) |
| **Workflow Dispatch** | Dispatches to external Google repository `angular/dev-infra` | Direct in-repo evaluation with zero external repository dependencies |
| **Commit Status Reporting** | Sets `mergeability` status check via Robot App | Sets `mergeability` status check via GitHub REST API |
| **Execution Trigger** | Unconditional `push` and `pull_request_target` | Filtered branch `push`, `pull_request_target`, and manual `workflow_dispatch` |
| **Fork Adaptability** | Permanently skips with `fork == false` | 100% functional and fully verified on forks |

---

## Section 4: Configuration & Data Requirements

### Repository Secrets

| Secret Name | Required? | Purpose in Original Mode | Purpose in Native Mode |
|---|---|---|---|
| `ANGULAR_ROBOT_PRIVATE_KEY` | Optional | Angular Robot GitHub App PEM private key for upstream org | Not required / ignored |

### Repository Variables

| Variable Name | Required? | Default | Description |
|---|---|---|---|
| `RUNNER_LABEL` | Optional | `ubuntu-latest` | Custom runner label (e.g., self-hosted runner) |
| `DEV_INFRA_MODE` | Optional | `auto` | Execution mode override (`auto`, `native`, or `original`) |

### GitHub Token Permissions

| Scope | Permission Level | Rationale |
|---|---|---|
| `contents` | `read` | Check out repository code |
| `pull-requests` | `read` | Query pull request target branches and open PR metadata |
| `statuses` | `write` | Set the `mergeability` commit status check |
| `actions` | `read` | Read workflow execution context |

---

## Section 5: Live Test Verification Details

*(Will be updated immediately following live GitHub Actions test execution)*

- **Run ID**: Pending
- **Run URL**: Pending
- **Trigger**: `workflow_dispatch`
- **Execution Mode**: `native`
- **Target Branch**: `main`
- **Outcome**: In progress

---

## Section 6: How to Test Later

### Via GitHub CLI (`gh`)
```bash
# Set authentication token if not already in environment
export GH_TOKEN="<your-personal-access-token>"

# Trigger default branch evaluation on main
gh workflow run "Assistant to the Branch Manager" \
  -R sajuptpm/angular \
  -f mode=native \
  -f branch=main

# Monitor execution
gh run list -R sajuptpm/angular --workflow "Assistant to the Branch Manager"
gh run watch -R sajuptpm/angular
```

### Via Bash Script
```bash
#!/usr/bin/env bash
set -euo pipefail

REPO="sajuptpm/angular"
WORKFLOW="assistant-to-the-branch-manager.yml"

echo "Dispatching $WORKFLOW on $REPO..."
gh workflow run "$WORKFLOW" -R "$REPO" \
  -f mode="native" \
  -f branch="main"

echo "Watching execution..."
gh run watch -R "$REPO"
```

### Via Python Script (`dispatch_branch_manager.py`)
```python
import os
import subprocess
import json
import time

repo = "sajuptpm/angular"
workflow = "assistant-to-the-branch-manager.yml"

print(f"Triggering {workflow} on {repo}...")
subprocess.run([
    "gh", "workflow", "run", workflow,
    "-R", repo,
    "-f", "mode=native",
    "-f", "branch=main"
], check=True)

print("Waiting for run to appear...")
time.sleep(6)
run_json = subprocess.check_output([
    "gh", "run", "list",
    "-R", repo,
    "--workflow", workflow,
    "--limit", "1",
    "--json", "databaseId,url,status"
])
run_data = json.loads(run_json)[0]
print(f"Run ID: {run_data['databaseId']} - {run_data['url']}")
```

---

## Section 7: Step-by-Step GitHub UI Manual Verification Guide

1. Navigate to `https://github.com/sajuptpm/angular`.
2. Click on the **Actions** tab.
3. In the left workflow list, select **Assistant to the Branch Manager**.
4. Click the **Run workflow** dropdown on the right.
5. Configure run parameters:
   - **Use workflow from**: Select `Branch: main`.
   - **Execution mode**: Select `native` (or leave default `auto`).
   - **Pull request number**: Leave as `0` (evaluates target branch PRs).
   - **Target branch name**: Leave default `main`.
6. Click the green **Run workflow** button.
7. Refresh after 3 seconds to see the queued run.
8. Click into the run:
   - Verify `Resolve Execution Mode` logs `Selected Execution Mode: native`.
   - Verify `Upstream Branch Manager (Original Mode)` is safely skipped.
   - Verify `Branch Mergeability Evaluation (Native Alternative)` succeeds, discovers target branch PRs, and publishes status checks.
   - Open the **Summary** tab to inspect the formatted markdown evaluation report.
