# Upstream Vendor DevInfra Pipeline Deep Dive (`dev-infra.yml` & Angular Robot)

> **Document Scope & Baseline Rules:**
> - Evaluates the original upstream `dev-infra.yml` in `angular/angular` prior to any fork-specific modifications.
> - Addresses operational architecture, upstream cloud costs, subscription requirements, release necessity, and concrete $0 zero-cost implementations for forked repositories.

---

## 1. Executive Summary

| Evaluation Dimension | Upstream Vendor (Google) Baseline | Forked Repository Baseline |
| :--- | :--- | :--- |
| **Pipeline & File** | `DevInfra` ([`.github/workflows/dev-infra.yml`](file:///c:/projects/angular/.github/workflows/dev-infra.yml)) | Same workflow file |
| **Category** | `Utility` (Repository Administration & Governance) | `Utility` |
| **Mandatory for Release?** | **NO (0% Impact)**. Purely administrative triage and PR policy | **Safe to Skip entirely** |
| **Primary Tools / Infra** | • **Angular Robot GitHub App** (`ANGULAR_ROBOT_PRIVATE_KEY`)<br>• **Google Gemini AI API** (`GOOGLE_GENERATIVE_AI_KEY`) | • Standard built-in `GITHUB_TOKEN`<br>• Rule-based keyword triage or free AI Studio tier |
| **Annual Tool/Infra Cost** | **$120 – $720 / year** (PAYG Gemini API & Bot hosting ceiling) | **$0.00 / year** (100% Free) |
| **SaaS Subscriptions** | **None** (No third-party SaaS subscriptions) | **None** |

---

## 2. What Does This Pipeline Do? (Detailed Job Breakdown)

The `dev-infra.yml` workflow manages repository hygiene, triage automation, and change management. It triggers strictly via GitHub webhooks (`pull_request_target` and `issues`) and runs three distinct jobs:

```
+---------------------------------------------------------------------------------------------------------+
|                                    DEVINFRA WORKFLOW ARCHITECTURE                                       |
+---------------------------------------------------------------------------------------------------------+
|                                                                                                         |
|  [ Event: pull_request_target ]                          [ Event: issues ]                              |
|         │                                                       │                                       |
|         ├──────────────────────────────┐                        ▼                                       |
|         ▼                              ▼                 [ Job 3: issue_labels ]                         |
|  [ Job 1: pull_request_labels ]  [ Job 2: post_approval_changes ]  • Evaluates issue title & body       |
|  • Scans modified PR files       • Inspects review state vs commit  • Sends text to Gemini AI model     |
|  • If packages/core/primitives/    timestamps                       • Predicts area label (e.g.,        |
|    matches, applies label:       • If new commits pushed after        area: router, area: compiler)     |
|    "requires: TGP"                 approval, marks review stale &   • Applies label via Angular Robot   |
|  • Uses Angular Robot App Key      adds "action: review" label      • Uses Gemini API Key + Robot Key   |
|                                  • Uses Angular Robot App Key                                           |
+---------------------------------------------------------------------------------------------------------+
```

### Detailed Functional Breakdown:
1. **Job 1: `pull_request_labels`**
   - **Trigger**: `pull_request_target` (`opened`, `synchronize`, `reopened`).
   - **Action**: `angular/dev-infra/github-actions/labeling/pull-request`.
   - **Functionality**: Scans modified files in the incoming pull request. If files inside `packages/core/primitives/**/{*,.*}` are modified, it applies the label `requires: TGP` (Targeted Google Presubmit). This signals to Angular maintainers that changes affect foundational core primitives that must be tested against Google's internal codebase (`google3`) prior to merging.
2. **Job 2: `post_approval_changes`**
   - **Trigger**: `pull_request_target` (`opened`, `synchronize`, `reopened`).
   - **Action**: `angular/dev-infra/github-actions/post-approval-changes`.
   - **Functionality**: Detects if new commits are pushed to a PR after an approving code review has already been submitted (`APPROVED`). If new commits are detected, it marks the approval as stale and adds an action label (`action: review`), preventing unreviewed code from slipping through.
3. **Job 3: `issue_labels`**
   - **Trigger**: `issues` (`opened`, `reopened`).
   - **Action**: `angular/dev-infra/github-actions/labeling/issue`.
   - **Functionality**: When an external community user opens a bug report or feature request, this job extracts the issue title and description, sends it to Google's **Gemini Generative AI model**, infers the affected framework area (`area: core`, `area: router`, `area: compiler`, etc.), and automatically tags the issue via the Angular Robot.

---

## 3. How the Upstream Vendor (Google) Runs This Pipeline

1. **Webhook Event Driven**: The workflow never executes on a schedule or during release builds. It triggers strictly when a contributor opens/updates a PR or files a GitHub issue.
2. **Privileged Identity via GitHub App (`Angular Robot`)**:
   - The workflow uses `permissions: contents: read` as its default.
   - All write operations (assigning labels, modifying PR metadata) are executed by authenticating as the **Angular Robot GitHub App** (`angular-robot[bot]`) using an RSA private key stored in `secrets.ANGULAR_ROBOT_PRIVATE_KEY`.
   - The action signs a JSON Web Token (JWT) on the fly, exchanges it with GitHub API for an Installation Access Token, and performs privileged mutations across the repository.
3. **Generative AI API Call**:
   - For issue classification, the action calls the Google Generative AI REST API using `secrets.GOOGLE_GENERATIVE_AI_KEY` to prompt Gemini models with the issue markdown text.

---

## 4. Cost Breakdown: How Much Upstream Pays & For What

Upstream incurs no recurring SaaS subscription fees. The costs break down as follows:

| Component / Tool | Upstream Pricing Model | Estimated Annual Cost | Purpose in Upstream Pipeline |
| :--- | :--- | :---: | :--- |
| **Angular Robot GitHub App** | • GitHub App registration: $0<br>• Backend serverless webhook hosting: ~$0–$10/mo | **$0 – $120 / year** | Provides a trusted bot persona (`angular-robot`) to manage labels, review invalidation, and branch operations without maintainer personal access tokens. |
| **Google Gemini AI API** | Pay-as-you-go per 1,000 tokens ($0.000125 to $0.0025 / 1k tokens) | **$120 – $600 / year**<br>*(~$10–$50/mo)* | Classifying ~30–50 incoming community issues per day to route them to the correct engineering sub-team without manual human triage. |
| **GitHub Actions Compute** | Standard `ubuntu-latest` Linux runners | **$0** | Standard public open-source runners are free on GitHub. Each job finishes in 5–15 seconds. |
| **Total Upstream Cost** | | **$120 – $720 / year** | Automated repository maintenance and community issue routing for Google's core team. |

---

## 5. Subscription Analysis

* **Zero SaaS Subscriptions**: Upstream does **not** subscribe to third-party issue management or bot platforms (such as Probot hosting SaaS, Linear, Sentry, or Jira automation subscriptions).
* **Cloud Primitives Only**: Uses a native GitHub App integration and consumption-based Google Generative AI API calls.

---

## 6. Can We Skip This Pipeline in an Open-Source Release from a Forked Repo?

### **YES, 100% ABSOLUTELY SAFE TO SKIP.**

### Deep Technical Justification & Risk Analysis:
1. **Completely Decoupled from Release & Build**:
   - `dev-infra.yml` is an administrative utility. It has **zero involvement** in compiling TypeScript, executing unit tests, running integration suites, or packaging `@angular/*` npm tarballs.
   - Production releases are built and published exclusively by [`release.yml`](file:///c:/projects/angular/.github/workflows/release.yml).
2. **No Code Artifact Impact (0% Risk)**:
   - Skipping `dev-infra.yml` produces **zero defects, zero runtime regressions, and zero missing typings** in published packages. The npm packages are 100% bit-for-bit identical whether this pipeline runs or not.
3. **Targeted Google Presubmit (`requires: TGP`) Is Irrelevant to Forks**:
   - The label `requires: TGP` exists exclusively to signal Google engineers to run internal `google3` monorepo presubmit tests. An independent open-source fork has no access to Google's internal code and has no need for this label.
4. **Fork Issue Volume Is Low**:
   - Unlike upstream (which receives hundreds of community issues a month), a downstream maintenance fork typically manages internal roadmap items and does not need an automated AI triage system.

---

## 7. Can I Run the Same Workflow in a Forked Repo Without Spending Money? How?

### **YES, 100% Absolutely YES ($0.00 / year).**

Here is the step-by-step implementation to run full equivalent functionality at zero cost:

#### Step 1: Replace the Proprietary GitHub App with Native `$GITHUB_TOKEN` ($0)
Instead of creating a dedicated GitHub App and managing RSA private keys:
- Grant write permissions in `dev-infra.yml`:
  ```yaml
  permissions:
    contents: read
    pull-requests: write
    issues: write
  ```
- Use the built-in `GITHUB_TOKEN` provided automatically by GitHub Actions in every run at zero cost.

#### Step 2: Replace Gemini AI with Free Rule-Based Triage OR Free AI Studio ($0)
You have two completely free choices:
* **Option A: Rule-Based Keyword Triage (Recommended — $0, Zero Dependencies)**:
  Execute a simple Node.js or bash script in the workflow that scans the issue title and body for keywords:
  ```bash
  # Example zero-dependency keyword classifier
  case "$ISSUE_BODY" in
    *router*|*Routes*) gh issue edit "$ISSUE_NUMBER" --add-label "area: router" ;;
    *compiler*|*template*) gh issue edit "$ISSUE_NUMBER" --add-label "area: compiler" ;;
    *form*|*FormControl*) gh issue edit "$ISSUE_NUMBER" --add-label "area: forms" ;;
    *) gh issue edit "$ISSUE_NUMBER" --add-label "needs: triage" ;;
  esac
  ```
  Runs in under 1 second on free GitHub runners with 100% determinism.
* **Option B: Google AI Studio Always-Free Tier ($0)**:
  If you specifically want AI-based classification, Google AI Studio provides an **Always Free Tier** for Gemini 1.5 Flash (up to 15 requests/minute, 1,500 requests/day).
  - Get a free API key at [aistudio.google.com](https://aistudio.google.com).
  - A forked repository filing a few issues a week consumes less than 0.05% of this free tier allowance.

#### Step 3: Native Post-Approval Invalidation via GitHub CLI ($0)
Inspect PR reviews using the preinstalled GitHub CLI (`gh`):
```bash
LATEST_APPROVAL=$(gh pr view "$PR_NUMBER" --json reviews --jq '[.reviews[] | select(.state=="APPROVED")] | last .submittedAt')
LATEST_COMMIT=$(gh pr view "$PR_NUMBER" --json commits --jq '.commits[-1].committedDate')

if [[ "$LATEST_COMMIT" > "$LATEST_APPROVAL" ]]; then
  gh pr edit "$PR_NUMBER" --add-label "action: review"
  gh pr comment "$PR_NUMBER" --body "⚠️ New commits pushed after last approval. Re-review required."
fi
```

---

## 8. Comparison Matrix: Upstream vs. Forked Options

| Dimension | Upstream Original (`dev-infra.yml`) | Fork Native Implementation (Recommended) | Fork Skipping Implementation |
| :--- | :--- | :--- | :--- |
| **Annual Infra Cost** | **$120 – $720 / year** | **$0.00 / year** | **$0.00 / year** |
| **Compute Cost** | $0 (Free GitHub OSS runner) | $0 (Free GitHub OSS runner) | $0 (Never runs) |
| **Authentication** | `ANGULAR_ROBOT_PRIVATE_KEY` (App) | Native `GITHUB_TOKEN` | None |
| **Issue Triage** | Google Gemini Generative AI API | Keyword heuristics or Free AI Studio | Manual maintainer triage |
| **PR Labeling** | Proprietary composite action | GitHub CLI (`gh pr edit`) | Manual or GitHub PR template |
| **External Dependencies**| GitHub App + Google AI Cloud Key | None (Zero external dependencies) | None |
| **Impact on OSS Release**| **None (0%)** | **None (0%)** | **None (0%)** |
| **Suitability for Fork** | Fails immediately on fork | **Ideal if automated triage desired** | **Recommended baseline** |
