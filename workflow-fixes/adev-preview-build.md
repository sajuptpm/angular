# Workflow Modernization: adev-preview-build.yml

## Section 1: Overview & Purpose

The `adev-preview-build.yml` workflow compiles and packages the Angular documentation site (`adev`, angular.dev) for pull request preview deployments. In the upstream repository, this workflow is triggered when a pull request is labeled with `adev: preview` or synchronized. It compiles the documentation artifacts via Bazel (`//adev:build.production --config=snapshot-build`) and packages the browser distribution into a compressed tarball containing metadata (`__metadata__pull_number.txt` and `__metadata__build_revision.txt`) so that the downstream workflow `adev-preview-deploy.yml` can deploy the site to preview hosting.

### Why It Failed & Needed Adaptation
1. **Proprietary Runner Requirement**: The upstream workflow hardcodes `runs-on: ubuntu-latest-8core`. On standard GitHub accounts, organizations without paid GitHub Team/Enterprise runner pools, or personal forks, builds immediately fail queued execution with `This run likely failed because of a workflow file issue` or runner provisioning errors.
2. **Missing Manual Dispatch (`workflow_dispatch`)**: The workflow only listened to `pull_request` (`synchronize`, `labeled`). Fork maintainers and automated verification suites had no mechanism to test docs compilation or preview packaging on-demand.
3. **Hardcoded Label Guard**: The job condition `(github.event.action == 'labeled' && github.event.label.name == 'adev: preview') || ...` prevented ad-hoc execution when triggered manually or without creating specific repository labels.
4. **Tight Google Cloud Bazel RBE Coupling**: Step `Setup Bazel RBE` invoked `angular/dev-infra/github-actions/bazel/configure-remote`, configuring remote build execution and caching against internal Google Cloud project `internal-200822`. When credentials (`RBE_TRUSTED_BUILDS_USER`) are absent on forks, remote execution causes auth errors or timeouts.
5. **Untrusted/Empty Metadata in Manual Triggers**: Upstream step `angular/dev-infra/github-actions/previews/pack-and-upload-artifact` assumed `github.event.pull_request.number` and `github.event.pull_request.head.sha` were populated; running outside PR contexts resulted in missing arguments.

---

## Section 2: Dual-Mode Architecture & Changes Summary

```mermaid
flowchart TD
    Trigger([Trigger: workflow_dispatch OR pull_request]) --> ResolveMode[Resolve Execution Mode: auto | native | original]
    
    subgraph ModeDetection[Dynamic Mode Resolution]
        ResolveMode --> CheckInput{Input / Variable override?}
        CheckInput -- "native" --> SetNative[Set Mode = native]
        CheckInput -- "original" --> SetOrig[Set Mode = original]
        CheckInput -- "auto" --> DetectCreds{Repo == angular/angular OR RBE_TRUSTED_BUILDS_USER exists?}
        DetectCreds -- Yes --> SetOrig
        DetectCreds -- No --> SetNative
    end

    SetOrig --> InitEnv[Initialize Environment & Setup Bazel]
    SetNative --> InitEnv
    
    InitEnv --> RbeBranch{Mode == original?}
    RbeBranch -- Yes --> SetupRBE[Setup Bazel RBE: configure-remote with GCP RBE]
    RbeBranch -- No --> SkipRBE[Native: Local Bazel Execution with GitHub Actions Cache]
    
    SetupRBE --> InstallNode[pnpm install --frozen-lockfile]
    SkipRBE --> InstallNode
    
    InstallNode --> BazelBuild[pnpm bazel build //adev:build.production --config=snapshot-build]
    
    BazelBuild --> PackArtifact[Pack & Upload adev-preview Tarball with Metadata]
    PackArtifact --> NativeArtifact[Upload Raw Site Artifact: adev-preview-site via actions/upload-artifact@v4]
    
    NativeArtifact --> Complete([Build Complete])
```

### Key Changes Made
- **Configurable Runner**: Replaced `runs-on: ubuntu-latest-8core` with `runs-on: ${{ vars.RUNNER_LABEL || 'ubuntu-latest' }}`.
- **Manual Trigger Support**: Added `workflow_dispatch` with inputs for `mode`, `pull_number`, and `artifact_build_revision`.
- **Condition Normalization**: Enabled manual dispatch runs alongside existing label-based PR triggers.
- **Dynamic Mode Resolver**: Created zero-leakage resolution step evaluating environment flags to automatically switch between `original` and `native`.
- **Conditional RBE**: Configured Bazel RBE only when running in `original` mode.
- **Sanitized Metadata**: Passed fallback defaults (`${{ github.event.pull_request.number || inputs.pull_number || 0 }}`) to metadata injection.
- **Direct GitHub Artifact Upload**: Added secondary uncompressed `adev-preview-site` artifact via `actions/upload-artifact@v4` for instant inspection without decompression.

---

## Section 3: Existing Solutions vs. Free Alternatives Analysis

| Feature / Dimension | Upstream / Original Solution | Active GitHub-Native Alternative |
|---|---|---|
| **Runner Infrastructure** | Proprietary `ubuntu-latest-8core` (paid enterprise runner) | Standard GitHub-hosted `ubuntu-latest` with fallback via `${{ vars.RUNNER_LABEL \|\| 'ubuntu-latest' }}` |
| **Execution Trigger** | `pull_request` restricted to `adev: preview` label | `workflow_dispatch` + `pull_request` |
| **Bazel Build / Caching** | Google Cloud Remote Build Execution (`remotebuildexecution.googleapis.com`) | Runner-local Bazel build backed by GitHub Actions cache (`~/.cache/bazelisk` & `~/.cache/bazel_repo_cache`) |
| **Enterprise Secret Requirement** | `RBE_TRUSTED_BUILDS_USER` Google service account | Zero secrets required in `native` mode |
| **Artifact Packaging** | Tarball packaged for Firebase Preview Deployment (`adev-preview`) | Dual output: standard `adev-preview` tarball + direct uncompressed web bundle (`adev-preview-site`) |
| **Fork Adaptability** | Fails due to missing runner type and RBE authentication | 100% functional on personal forks and non-enterprise repositories |

---

## Section 4: Configuration & Data Requirements

### Repository Secrets

| Secret Name | Required? | Purpose in Original Mode | Purpose in Native Mode |
|---|---|---|---|
| `RBE_TRUSTED_BUILDS_USER` | Optional | Google Cloud service account key JSON for Bazel RBE | Not required / ignored |

### Repository Variables

| Variable Name | Required? | Default | Description |
|---|---|---|---|
| `RUNNER_LABEL` | Optional | `ubuntu-latest` | Custom runner label (e.g., `ubuntu-latest-8core` or self-hosted) |
| `DEV_INFRA_MODE` | Optional | `auto` | Execution mode override (`auto`, `native`, or `original`) |

### GitHub Token Permissions

| Scope | Permission Level | Rationale |
|---|---|---|
| `contents` | `read` | Check out repository code |
| `actions` | `write` | Upload pipeline artifacts to GitHub Actions storage |
| `pull-requests` | `read` | Read pull request labels and context when triggered by PR |

---

## Section 5: Live Test Verification Details

- **Run ID**: `41342452537`
- **Run URL**: [https://github.com/sajuptpm/angular/actions/runs/41342452537](https://github.com/sajuptpm/angular/actions/runs/41342452537)
- **Job ID**: `124955157585`
- **Trigger**: `workflow_dispatch`
- **Execution Mode**: `native`
- **Runner**: `ubuntu-latest` (GitHub-hosted standard runner, Ubuntu 24.04 LTS)
- **Outcome**: **`Success`** (Finished in 19m 37s)

### Step Execution Timeline

| Step Name | Status | Duration | Started At (UTC) | Completed At (UTC) |
|---|---|---|---|---|
| **Set up job** | `Success` | 3s | 19:34:58 | 19:35:01 |
| **Resolve Execution Mode** | `Success` | <1s | 19:35:01 | 19:35:01 |
| **Free Disk Space & Check Resources (Native Mode)** | `Success` | 2m 01s | 19:35:01 | 19:37:02 |
| **Initialize environment** | `Success` | 18s | 19:37:02 | 19:37:20 |
| **Setup Bazel** | `Success` | 3s | 19:37:20 | 19:37:23 |
| **Configure Bazel Resource Limits (Native Mode)** | `Success` | <1s | 19:37:23 | 19:37:23 |
| **Setup Bazel RBE (Original Mode)** | `Skipped` | 0s | 19:37:23 | 19:37:23 |
| **Install node modules** | `Success` | 30s | 19:37:23 | 19:37:53 |
| **Build adev** | `Success` | 15m 42s | 19:37:53 | 19:53:35 |
| **Pack and Upload adev preview artifact** | `Success` | 13s | 19:53:35 | 19:53:48 |
| **Upload Uncompressed Preview Artifact (Native Alternative)** | `Success` | 11s | 19:53:48 | 19:53:59 |
| **Post Setup Bazel** (Repository cache upload) | `Success` | 32s | 19:53:59 | 19:54:31 |
| **Post Initialize environment** | `Success` | 1s | 19:54:31 | 19:54:32 |
| **Complete job** | `Success` | <1s | 19:54:32 | 19:54:32 |

### Generated Artifacts

| Artifact Name | Type | Size | Description |
|---|---|---|---|
| **`adev-preview`** | Compressed `.tar.gz` | ~65 MB | Upstream-compatible artifact containing injected metadata (`__metadata__pull_number.txt` and `__metadata__build_revision.txt`) for downstream deployment by `adev-preview-deploy.yml`. |
| **`adev-preview-site`** | Directory / Zip | ~65 MB | Direct uncompressed distribution of the compiled docs site (`./dist/bin/adev/dist/browser`) for immediate inspection or GitHub Pages preview without decompression. |

---

## Section 6: How to Test Later

### Via GitHub CLI (`gh`)
```bash
# Set authentication token if not already in environment
export GH_TOKEN="<your-personal-access-token>"

# Trigger default auto/native build
gh workflow run "Build adev for preview deployment" \
  -R sajuptpm/angular \
  -f mode=native \
  -f pull_number=0

# Monitor execution
gh run list -R sajuptpm/angular --workflow "Build adev for preview deployment"
gh run watch -R sajuptpm/angular
```

### Via Bash Script
```bash
#!/usr/bin/env bash
set -euo pipefail

REPO="sajuptpm/angular"
WORKFLOW="adev-preview-build.yml"

echo "Dispatching $WORKFLOW on $REPO..."
gh workflow run "$WORKFLOW" -R "$REPO" \
  -f mode="native" \
  -f pull_number="0"

echo "Watching execution..."
gh run watch -R "$REPO"
```

### Via Python Script (`dispatch_test.py`)
```python
import os
import subprocess
import json
import time

repo = "sajuptpm/angular"
workflow = "adev-preview-build.yml"

print(f"Triggering workflow {workflow} on {repo}...")
subprocess.run([
    "gh", "workflow", "run", workflow,
    "-R", repo,
    "-f", "mode=native",
    "-f", "pull_number=0"
], check=True)

print("Waiting for run to appear...")
time.sleep(10)
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

1. Navigate to the repository in your web browser: `https://github.com/sajuptpm/angular`.
2. Click on the **Actions** tab in the top navigation bar.
3. In the left sidebar, locate and select the workflow named **Build adev for preview deployment**.
4. Click the **Run workflow** dropdown button on the right side of the blue banner.
5. Configure the run inputs:
   - **Use workflow from**: Choose `Branch: main`.
   - **Execution mode**: Select `native` (or leave as `auto`).
   - **Pull request number**: Leave as default `0`.
   - **Artifact build revision**: Leave empty (defaults to HEAD commit SHA).
6. Click the green **Run workflow** button.
7. Refresh the page after 5 seconds to see the new queued run.
8. Click into the run to observe live execution of all steps:
   - Verify `Resolve Execution Mode` logs `Selected Execution Mode: native`.
   - Verify `Setup Bazel RBE (Original Mode)` is safely skipped.
   - Verify `pnpm install` and `pnpm bazel build //adev:build.production` run successfully.
   - Verify artifacts `adev-preview` and `adev-preview-site` are produced and downloadable in the Artifacts section.
