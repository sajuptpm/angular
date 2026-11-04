# Angular Infrastructure and Tooling Cost Estimation (Original Upstream Baseline)

> **Document Scope & Baseline Rules:**
> - Evaluates the **Angular repository (`angular/angular`)** based strictly on the original upstream workflow definitions (prior to dual-mode / fallback modifications).
> - Populated in **`Sheet1`** of [`workflow-fixes/infra_tool_estimate.xlsx`](file:///c:/projects/angular/workflow-fixes/infra_tool_estimate.xlsx).
> - Rate formulas, cost assumptions, and planning determinations are aligned with **`Sheet2`**, **`Sheet3`**, and project baseline cost rules.
> - **Component Column**: `angular`
> - **Categories**: `Build`, `Package`, `Test`, `Release Doc`, `Release`, `Internal to Vendor`, `Utility`.
> - **Mandatory Column (`Yes`/`No`)**: Identifies whether the specific workflow and tool are mandatory for operating an independent forked repository producing open-source framework releases.

---

## 1. Executive Summary & Total Cost Overview

In the original upstream Angular configuration, Google maintains large-scale distributed build acceleration (Google Cloud RBE), automated cross-browser cloud farms (SauceLabs), AI-based issue triage (Google Gemini API), production documentation hosting (Google Firebase Hosting & Algolia DocSearch), telemetry metric lakes (GCP BigQuery & Cloud Storage), and internal monorepo synchronization gates (Google3 / TAP).

When operating an **independent forked repository and open-source release model**:
1. **Mandatory Pipelines (`Yes`)**:
   - `pr.yml` (Pull Request validation: unit tests, integration tests, devtools, Zone.js).
   - `ci.yml` (Post-merge verification: package compilation, core test suite, snapshot validation).
   - `release.yml` (Production artifact publishing: `@angular/*` scoped packages to npm with provenance).
   - `run-saucelabs-tests.sh` (Browser compatibility and real-device runtime qualification).
2. **Non-Mandatory Pipelines (`No`)**:
   - `adev-preview-build.yml` & `adev-preview-deploy.yml` (PR preview staging on Firebase).
   - `perf.yml` (Continuous historical telemetry ingestion into Google's internal BigQuery).
   - `dev-infra.yml` & `assistant-to-the-branch-manager.yml` (Issue auto-labeling, branch cherry-pick automation).
   - `google-internal-tests.yml` (Google3 proprietary presubmit gate).
   - `benchmark-compare.yml` (Ad-hoc PR comment performance comparisons).
   - `cross-repo-adev-docs.yml` (Synchronization of docs across upstream satellite repositories).

### Annual Cost Breakdown for Fork Baseline

| Infra / Tool Item | Upstream Pricing Model | Usage Assumption | Yearly Cost ($) | Planning Status in Fork |
| :--- | :--- | :--- | :--- | :--- |
| **Google Cloud Remote Build Execution (RBE)** | PAYG GCP: \$500–\$2,500/mo | Upstream monorepo build acceleration | **Not Planning / Replacement** | Skip/Replace with local Bazel cache |
| **GitHub Larger Runners (`ubuntu-latest-8core`)** | PAYG: \$0.032/min | 50 runs/mo × 30 min/run ≈ \$48/mo | **\$576** | Retained for heavy builds & docs |
| **SauceLabs / BrowserStack Cloud Grid** | SaaS Subscription: \$199–\$999/mo | Release qualification, 4–8 cycles/PI | **\$2,400** (or \$600 targeted) | Retained for runtime certification |
| **Algolia DocSearch / Search API** | Commercial Tier: \$100–\$500/mo | Public documentation search index | **Not Planning / Replacement** | Skip or use Pagefind/Free Tier |
| **Google Gemini AI API** | PAYG API: \$10–\$100/mo | Automated community issue triage | **Not Planning / Replacement** | Skip; fork traffic is low |
| **Google Firebase Hosting & Preview Channels** | Storage & Bandwidth: \$10–\$50/mo | Release documentation hosting | **\$120** | Retained if hosting docs portal |
| **GCP Telemetry (BigQuery & Cloud Storage)** | PAYG: \$10–\$30/mo | Historical telemetry & benchmark tracking | **Not Planning / Replacement** | Skip; local reports suffice |
| **GitHub Standard Runners (`ubuntu-latest`)** | Free for public repos; \$0.008/min private | ~300 builds/mo × 10 min/build | **\$288** (or \$0 for public) | Standard CI compute |
| **npm Public Registry Scoped Publishing** | Free for public OSS | Production package publishing | **\$0** | Retained for public package distribution |
| **Open Source Toolchain (Bazel, Node.js, pnpm, etc.)** | Open Source (Free) | All workflows | **\$0** | Core build/test toolchain |
| **Angular Robot GitHub App / Tokens** | GitHub App / Tokens (Free) | Automation and release orchestration | **\$0** | Replaced with native GITHUB_TOKEN |
| **Google Internal Monorepo Infrastructure (TAP/G3)** | Proprietary Google internal | Inaccessible outside Google network | **\$0** | Skipped entirely |
| **Total Annual Cost** | | | **\$3,384** (or \$1,584 targeted) | |

---

## 2. Complete Inventory: Sheet1 of `infra_tool_estimate.xlsx`

Below is the complete dataset populated in **`Sheet1`** of [`workflow-fixes/infra_tool_estimate.xlsx`](file:///c:/projects/angular/workflow-fixes/infra_tool_estimate.xlsx):

| Component | Pipeline | Description | Category | Mandatory | Infra | Cost basis | Yearly Cost |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- | :---: |
| `angular` | `pr.yml` | Validates incoming pull requests with linting, unit tests, integration tests, and compilation checks across the Angular monorepo | `Test` | **Yes** | Google Cloud Remote Build Execution (RBE) | PAYG GCP Service: ~$500–$2,500/month (~$6K–$30K/year) | Not Planning / Replacement |
| `angular` | `pr.yml` | Validates incoming pull requests with linting, unit tests, integration tests, and compilation checks across the Angular monorepo | `Test` | **Yes** | GitHub Standard Runners (ubuntu-latest) | Free for public repos; ~$0.008/min for private repos (~$24/month) | \$288 |
| `angular` | `pr.yml` | Validates incoming pull requests with linting, unit tests, integration tests, and compilation checks across the Angular monorepo | `Test` | **Yes** | Open Source Toolchain (Bazel, Node.js, pnpm, TypeScript, Jasmine, Karma, Cypress) | Open Source (Free) | \$0 |
| `angular` | `ci.yml` | Executes post-merge CI verification on main/release branches, builds packages, runs tests, creates snapshot builds, and deploys documentation | `Build` | **Yes** | Google Cloud Remote Build Execution (RBE) | PAYG GCP Service: ~$500–$2,500/month (~$6K–$30K/year) | Not Planning / Replacement |
| `angular` | `ci.yml` | Executes post-merge CI verification on main/release branches, builds packages, runs tests, creates snapshot builds, and deploys documentation | `Build` | **Yes** | GitHub Larger Runners (ubuntu-latest-8core) | PAYG GitHub Runners: ~$0.032/min (50 runs/month × 30 min ≈ $48/month) | \$576 |
| `angular` | `ci.yml` | Executes post-merge CI verification on main/release branches, builds packages, runs tests, creates snapshot builds, and deploys documentation | `Build` | **Yes** | GitHub Standard Runners (ubuntu-latest) | Free for public repos; ~$0.008/min for private repos | Included in standard runner pool |
| `angular` | `ci.yml` | Executes post-merge CI verification on main/release branches, builds packages, runs tests, creates snapshot builds, and deploys documentation | `Release Doc` | **No** | Google Firebase Hosting & Preview Channels | Storage & Bandwidth Billing: ~$10–$50/month (~$120–$600/year) | \$120 |
| `angular` | `ci.yml` | Executes post-merge CI verification on main/release branches, builds packages, runs tests, creates snapshot builds, and deploys documentation | `Release Doc` | **No** | Algolia DocSearch / Search API | Commercial Tier ~$100–$500/month (Free OSS tier available) | Not Planning / Replacement |
| `angular` | `ci.yml` | Executes post-merge CI verification on main/release branches, builds packages, runs tests, creates snapshot builds, and deploys documentation | `Package` | **Yes** | Open Source Toolchain (Bazel, Node.js, pnpm, Rollup, Terser, TypeScript) | Open Source (Free) | \$0 |
| `angular` | `release.yml` | Compiles, validates, and publishes production @angular/* release packages, npm provenance, and tags | `Release` | **Yes** | GitHub Standard Runners (ubuntu-latest) | Free for public repos; ~$0.008/min for private repos | Included in standard runner pool |
| `angular` | `release.yml` | Compiles, validates, and publishes production @angular/* release packages, npm provenance, and tags | `Package` | **Yes** | npm Public Registry Scoped Publishing | Public OSS Publishing = Free | \$0 |
| `angular` | `release.yml` | Compiles, validates, and publishes production @angular/* release packages, npm provenance, and tags | `Release` | **Yes** | Angular Robot GitHub App (ANGULAR_ROBOT_PRIVATE_KEY) | GitHub App + Cloud Function host: ~$10–$25/month (Free on GitHub native) | \$0 |
| `angular` | `release.yml` | Compiles, validates, and publishes production @angular/* release packages, npm provenance, and tags | `Build` | **Yes** | Open Source Toolchain (Bazel, Node.js, pnpm, Rollup, Terser) | Open Source (Free) | \$0 |
| `angular` | `adev-preview-build.yml` | Compiles and packages angular.dev documentation site for pull request preview deployment when labeled | `Release Doc` | **No** | GitHub Larger Runners (ubuntu-latest-8core) | PAYG GitHub Runners: ~$0.032/min (~$48/month) | Included in Larger Runner line (\$576) |
| `angular` | `adev-preview-build.yml` | Compiles and packages angular.dev documentation site for pull request preview deployment when labeled | `Release Doc` | **No** | Google Cloud Remote Build Execution (RBE) | PAYG GCP Service: ~$500–$2,500/month (~$6K–$30K/year) | Not Planning / Replacement |
| `angular` | `adev-preview-build.yml` | Compiles and packages angular.dev documentation site for pull request preview deployment when labeled | `Release Doc` | **No** | Open Source Toolchain (Bazel, Node.js, pnpm) | Open Source (Free) | \$0 |
| `angular` | `adev-preview-deploy.yml` | Deploys compiled documentation preview bundle to Google Firebase Hosting preview channels | `Release Doc` | **No** | Google Firebase Hosting & Preview Channels (ng-dev-previews) | Storage & Bandwidth Billing: ~$10–$50/month (~$120–$600/year) | Included in Firebase Hosting line (\$120) |
| `angular` | `adev-preview-deploy.yml` | Deploys compiled documentation preview bundle to Google Firebase Hosting preview channels | `Release Doc` | **No** | GitHub Standard Runners (ubuntu-latest) | Free for public repos; ~$0.008/min for private repos | Included in standard runner pool |
| `angular` | `perf.yml` | Measures framework bundle size, runs benchmarks, and tracks telemetry regressions across commits | `Test` | **No** | GCP Telemetry (BigQuery & Cloud Storage) | PAYG Storage & Queries: ~$10–$30/month (~$120–$360/year) | Not Planning / Replacement |
| `angular` | `perf.yml` | Measures framework bundle size, runs benchmarks, and tracks telemetry regressions across commits | `Test` | **No** | Google Cloud Workload Identity Federation (WIF) | Feature of GCP Cloud IAM: $0 | \$0 |
| `angular` | `perf.yml` | Measures framework bundle size, runs benchmarks, and tracks telemetry regressions across commits | `Test` | **No** | GitHub Standard Runners (ubuntu-latest) | Free for public repos; ~$0.008/min for private repos | Included in standard runner pool |
| `angular` | `dev-infra.yml` | Automates issue classification, PR label assignment, and review change tracking via Angular dev-infra bots | `Utility` | **No** | Google Gemini AI API (GOOGLE_GENERATIVE_AI_KEY) | PAYG API: ~$10–$100/month ($0.000125–$0.0025/1k tokens) | Not Planning / Replacement |
| `angular` | `dev-infra.yml` | Automates issue classification, PR label assignment, and review change tracking via Angular dev-infra bots | `Utility` | **No** | Angular Robot GitHub App (ANGULAR_ROBOT_PRIVATE_KEY) | GitHub App + Cloud Function host: ~$10–$25/month | \$0 |
| `angular` | `dev-infra.yml` | Automates issue classification, PR label assignment, and review change tracking via Angular dev-infra bots | `Utility` | **No** | GitHub Standard Runners (ubuntu-latest) | Free for public repos; ~$0.008/min for private repos | Included in standard runner pool |
| `angular` | `assistant-to-the-branch-manager.yml` | Validates PR mergeability across release branches, monitors cherry-pick requirements, and sets branch statuses | `Utility` | **No** | Angular Robot GitHub App (ANGULAR_ROBOT_PRIVATE_KEY) | GitHub App + Cloud Function host: ~$10–$25/month | \$0 |
| `angular` | `assistant-to-the-branch-manager.yml` | Validates PR mergeability across release branches, monitors cherry-pick requirements, and sets branch statuses | `Utility` | **No** | GitHub Standard Runners (ubuntu-latest) | Free for public repos; ~$0.008/min for private repos | Included in standard runner pool |
| `angular` | `google-internal-tests.yml` | Synchronizes changes and triggers presubmit verification against Google internal private monorepo (Google3 / TAP) | `Internal to Vendor` | **No** | Google Internal Monorepo Infrastructure (Google3 / TAP) | Proprietary Google-internal infrastructure (inaccessible externally) | \$0 |
| `angular` | `google-internal-tests.yml` | Synchronizes changes and triggers presubmit verification against Google internal private monorepo (Google3 / TAP) | `Internal to Vendor` | **No** | GitHub Standard Runners (ubuntu-latest) | Free for public repos; ~$0.008/min for private repos | Included in standard runner pool |
| `angular` | `benchmark-compare.yml` | Compares performance benchmarks on demand between a PR branch and a base commit triggered by PR comments | `Test` | **No** | Google Cloud Remote Build Execution (RBE) | PAYG GCP Service: ~$500–$2,500/month (~$6K–$30K/year) | Not Planning / Replacement |
| `angular` | `benchmark-compare.yml` | Compares performance benchmarks on demand between a PR branch and a base commit triggered by PR comments | `Test` | **No** | GitHub Standard Runners (ubuntu-latest) | Free for public repos; ~$0.008/min for private repos | Included in standard runner pool |
| `angular` | `benchmark-compare.yml` | Compares performance benchmarks on demand between a PR branch and a base commit triggered by PR comments | `Test` | **No** | GitHub API Bot Tokens (BENCHMARK_POST_RESULTS_GITHUB_TOKEN) | GitHub Personal Access Token / App: Free | \$0 |
| `angular` | `cross-repo-adev-docs.yml` | Ingests and synchronizes documentation content from external Angular repositories (angular-cli, components) | `Release Doc` | **No** | Angular Robot GitHub App / Token (ANGULAR_ROBOT_ACCESS_TOKEN) | GitHub Personal Access Token / App: Free | \$0 |
| `angular` | `cross-repo-adev-docs.yml` | Ingests and synchronizes documentation content from external Angular repositories (angular-cli, components) | `Release Doc` | **No** | GitHub Standard Runners (ubuntu-latest) | Free for public repos; ~$0.008/min for private repos | Included in standard runner pool |
| `angular` | `run-saucelabs-tests.sh` | Cross-browser and real-device validation for Angular runtime, Zone.js, DOM events, and browser compatibility | `Test` | **Yes** | SauceLabs / BrowserStack Cloud Grid | SaaS Subscription: ~$199–$999/month (~$2.4K–$12K/year; targeted: ~$600/year) | \$2,400 (minimum planning) |
| `angular` | `run-saucelabs-tests.sh` | Cross-browser and real-device validation for Angular runtime, Zone.js, DOM events, and browser compatibility | `Test` | **Yes** | Open Source Toolchain (Karma, Jasmine, Playwright, Chrome Headless) | Open Source (Free) | \$0 |

---

## 3. Deep Analysis of "Not Planning / Replacement" Infrastructure

Five upstream tools/infrastructure components are designated as **"Not Planning / Replacement"**. The table below evaluates the impact on forked pipelines and release viability:

```
+---------------------------------------------------------------------------------------------------+
| Infra / Tool          | Affected Pipelines   | Impact / Risk on Fork Pipelines & Open-Source Releases    | Safe to Skip?  |
+---------------------------------------------------------------------------------------------------+
| Google Cloud Remote   | pr.yml, ci.yml,      | Build times increase (clean builds take ~25-40 min vs.    | Safe to Skip / |
| Build Execution (RBE) | adev-preview-build,  | 5-8 min with RBE). No compilation errors or package bugs. | Replace with   |
|                       | benchmark-compare    | Replaced seamlessly with GitHub Actions cache / Bazel.   | Local Cache    |
+---------------------------------------------------------------------------------------------------+
| Algolia DocSearch /   | ci.yml (adev-deploy) | Documentation search index is not updated in Algolia.     | Safe to Skip   |
| Search API            |                      | No impact on runtime packages or release distribution.    | (Docs Only)    |
|                       |                      | Optional replacement: Pagefind or Lunr.js.                |                |
+---------------------------------------------------------------------------------------------------+
| Google Gemini AI API  | dev-infra.yml        | Triage bot does not auto-label new issues with AI.        | Safe to Skip   |
|                       |                      | Zero impact on build, test, or package releases.          | (Triage Only)  |
+---------------------------------------------------------------------------------------------------+
| GCP Telemetry         | perf.yml             | Benchmark metrics are not uploaded to Google's BigQuery.  | Safe to Skip   |
| (BigQuery / Storage)  |                      | Release artifacts and NPM packages are completely unaffected.| (Telemetry Only)|
+---------------------------------------------------------------------------------------------------+
| Google3 / TAP Presubmit| google-internal-    | Presubmit sync against Google's private monorepo is skipped| Safe to Skip  |
|                       | tests.yml            | Completely Google-internal; public OSS releases require   | (Vendor Only)  |
|                       |                      | no internal Google sync.                                  |                |
+---------------------------------------------------------------------------------------------------+
```

---

## 4. Verification and Integrity Check

1. **Workbook File**: `workflow-fixes/infra_tool_estimate.xlsx`
2. **Sheet**: `Sheet1`
3. **Total Data Rows**: 35 rows (Row 2 to Row 36)
4. **Zero Missing Data**: Verified with Python that all cells have non-null, valid values matching Sheet2/Sheet3 specifications.
5. **Column Formatting**:
   - Column 1: `Component` = `angular` (centered)
   - Column 2: `Pipeline` = Workflow file name (left-aligned)
   - Column 3: `Description` = Detailed workflow purpose (left-aligned)
   - Column 4: `Category` = `Build`, `Package`, `Test`, `Release Doc`, `Release`, `Internal to Vendor`, `Utility` (centered)
   - Column 5: `Mandatory` = `Yes` / `No` (bold, centered)
   - Column 6: `Infra` = Tool / Infra name (left-aligned)
   - Column 7: `Cost basis` = Pricing formula and unit rates (left-aligned)
   - Column 8: `Yearly Cost` = Yearly figure or status (bold, centered)
