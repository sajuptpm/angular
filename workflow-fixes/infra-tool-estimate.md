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


---

# Upstream Vendor Performance Tracking Pipeline Deep Dive (`perf.yml` & BigQuery)

> **Document Scope & Baseline Rules:**
> - Evaluates the original upstream `perf.yml` in `angular/angular` prior to any fork-specific modifications.
> - Addresses operational architecture, upstream cloud costs, subscription requirements, and concrete $0 zero-cost implementations for forked repositories.

---

## 1. Executive Summary

| Evaluation Dimension | Upstream Vendor (Google) Baseline | Forked Repository Baseline |
| :--- | :--- | :--- |
| **Pipeline & File** | `Performance Tracking` ([`.github/workflows/perf.yml`](file:///c:/projects/angular/.github/workflows/perf.yml)) | Same workflow file |
| **Execution Trigger** | Unconditional `push` on branch `main` | `push` or `workflow_dispatch` (on-demand) |
| **Primary Cloud Tool** | **Google Cloud BigQuery** & Cloud Storage (GCS) | GitHub Actions Artifacts & Step Summary (or GCP Free Tier) |
| **Authentication** | Google Cloud Workload Identity Federation (WIF / OIDC) | None required (GitHub native) or custom free GCP WIF |
| **Annual Cloud Cost** | **$120 – $360 / year** (PAYG BigQuery storage/queries) | **$0.00 / year** (100% Free) |
| **SaaS Subscriptions** | **None** (No third-party SaaS tools like Datadog/New Relic) | **None** |
| **Necessity for Release** | **No (0% Impact)**. Purely outbound telemetry tracking | **Optional**; does not gate or affect npm package releases |

---

## 2. How the Upstream Vendor (Google) Runs This Pipeline

In the original upstream repository (`angular/angular`), the performance tracking pipeline operates through a two-stage automated workflow:

```
+---------------------------------------------------------------------------------------------------------+
|                                    UPSTREAM GOOGLE EXECUTION FLOW                                        |
+---------------------------------------------------------------------------------------------------------+
|                                                                                                         |
|  [ Event: git push to main ]                                                                            |
|         │                                                                                               |
|         ▼                                                                                               |
|  [ Job 1: list ] (Runs on ubuntu-latest)                                                                |
|         │                                                                                               |
|         ├─▶ Environment setup: Node.js, pnpm install --frozen-lockfile                                  |
|         ├─▶ Discovery command: pnpm --silent ng-dev perf workflows --list                               |
|         │   (Parses .ng-dev/dx-perf-workflows.yml and framework measurables)                             |
|         └─▶ Emits JSON matrix output: ['build-adev', ...]                                                |
|         │                                                                                               |
|         ▼                                                                                               |
|  [ Job 2: workflow matrix ] (Parallel fan-out per discovered target, 30-min timeout)                     |
|         │                                                                                               |
|         ├─▶ Step 1: Environment & Toolchain: Node.js, pnpm, and Bazel setup                             |
|         │                                                                                               |
|         ├─▶ Step 2: Keyless GCP OIDC Authentication via Workload Identity Federation (WIF)               |
|         │     • Action: google-github-actions/auth@v3                                                   |
|         │     • Project ID: internal-200822 (Google internal Angular CI project)                        |
|         │     • Identity Pool: projects/823469418460/locations/global/workloadIdentityPools/...         |
|         │     • Provider: providers/angular                                                             |
|         │     • Service Account: measures-uploader@internal-200822.iam.gserviceaccount.com             |
|         │                                                                                               |
|         └─▶ Step 3: Benchmark Execution & Cloud Streaming                                               |
|               • Command: pnpm ng-dev perf workflows --name "$WORKFLOW" --commit-sha "$COMMIT_SHA"     |
|               • Executes benchmark targets (e.g., bazel clean && bazel build //adev:build)              |
|               • Records wall-clock duration, memory usage, and output artifact bundle sizes             |
|               • Streams structured rows directly into Google BigQuery tables                            |
|               • Uploads raw profiling traces and memory graphs to Google Cloud Storage (GCS)            |
+---------------------------------------------------------------------------------------------------------+
```

### Upstream Security & Identity Binding
Upstream uses **Workload Identity Federation (WIF)** to eliminate static Service Account JSON keys:
1. GitHub Actions generates a signed OIDC JWT token (`id-token: write`) containing the repository identity.
2. The token is sent to Google Cloud STS (`https://sts.googleapis.com`).
3. Google Cloud evaluates the identity condition configured on the provider:
   `assertion.repository == 'angular/angular' && assertion.ref == 'refs/heads/main'`
4. Upon validation, STS returns a short-lived GCP OAuth2 access token mapped to `measures-uploader@internal-200822.iam.gserviceaccount.com`.

---

## 3. Cost Analysis: How Much Upstream Pays & For What

Google incurs no subscription fees for this pipeline; all expenses are consumption-based within Google Cloud Platform and GitHub:

| Service / Infrastructure | Rate / Cost Basis | Yearly Billed Cost ($) | Purpose & Usage Justification |
| :--- | :--- | :---: | :--- |
| **GitHub Actions Compute** | Standard `ubuntu-latest` Linux runners | **$0** *(Public OSS)* | GitHub provides free runner minutes for public open-source repositories. (If billed privately at $0.008/min, ~3,000 min/mo = ~$288/year). |
| **Google Cloud WIF (IAM)** | Keyless STS token exchange | **$0** | Native GCP security service included at no extra charge. |
| **Google Cloud BigQuery** | • Streaming inserts: $0.05 / GiB<br>• Active storage: $0.02 / GiB / month<br>• Analytical queries: $6.25 / TiB scanned | **$120 – $360 / year**<br>*(~$10–$30/month)* | • **Long-term historical telemetry**: Archiving bundle sizes and compile timings across every commit over years.<br>• **Cross-version regression queries**: Running SQL queries to identify commits causing bundle bloat.<br>• **Dashboards**: Live metric feeds for Google internal Looker Studio dashboards. |
| **Google Cloud Storage (GCS)** | Standard Storage: $0.020–$0.026 / GiB / month | **$12 – $24 / year**<br>*(~$1–$2/month)* | Storing raw benchmark traces, profile logs, and dependency graph measurables. |
| **Total Upstream Spend** | | **$132 – $384 / year** | Absorbed via Google's internal Cloud billing project `internal-200822`. |

---

## 4. Subscription Analysis

* **Zero SaaS Subscriptions**: There are **no active SaaS subscriptions** (e.g., Datadog, New Relic, Dynatrace, Honeycomb, or commercial APM solutions) in this pipeline.
* **Pure Cloud Primitives**: The pipeline relies entirely on basic serverless cloud primitives (IAM, BigQuery, GCS) within GCP.

---

## 5. Why the Unmodified Upstream Workflow Fails on a Forked Repo

When an unmodified upstream `perf.yml` runs on an external fork (`<fork-org>/angular`):
1. **GCP OIDC Rejection (`403 Forbidden`)**:
   GitHub Actions presents an OIDC token with `sub: repo:<fork-org>/angular:ref:refs/heads/main`. Because Google's WIF trust policy strictly requires `assertion.repository == 'angular/angular'`, Google's STS rejects the token exchange.
2. **Missing Service Account Access**:
   The workflow lacks write access to `measures-uploader@internal-200822.iam.gserviceaccount.com`.
3. **Fatal Pipeline Crash**:
   Step `google-github-actions/auth` terminates immediately with exit code 1, causing the entire workflow to fail.

---

## 6. How to Run This Workflow in a Forked Repo for $0 (Zero Dollars)

You can run complete performance and bundle size tracking on a forked repository without paying anything.

### Option A: GitHub-Native File & Artifact Storage (Recommended — $0/year)

This option replaces external cloud telemetry with built-in GitHub features, requiring **zero cloud accounts and zero external configuration**:

1. **Leverage Free Runner Minutes ($0)**:
   Public repositories on GitHub Enterprise / GitHub.com receive unlimited free execution on standard `ubuntu-latest` runners.
2. **Remove / Bypass Google Cloud Authentication**:
   Omit the `google-github-actions/auth` step, or wrap it in a conditional check (`if: env.ENABLE_GCP_METRICS == 'true'`).
3. **Capture Benchmark Outputs Locally**:
   Execute the benchmark commands locally on the runner:
   ```bash
   pnpm bazel build //adev:build
   ```
   Inspect generated bundle sizes directly using standard shell utilities (`stat -c %s dist/bin/...` or Node.js scripts) and write the results to a JSON file (`perf-report.json`).
4. **Publish as Downloadable GitHub Actions Artifact ($0)**:
   Use the official, free `actions/upload-artifact@v4`:
   ```yaml
   - name: Upload Performance Report
     uses: actions/upload-artifact@v4
     with:
       name: perf-report-${{ matrix.workflow }}
       path: ./perf-report.json
       retention-days: 90
   ```
5. **Render Inline Step Summary ($0)**:
   Append formatted Markdown directly to `$GITHUB_STEP_SUMMARY`:
   ```bash
   echo "### ⚡ Performance & Bundle Size Report" >> $GITHUB_STEP_SUMMARY
   echo "| Target | Size (bytes) | Build Duration |" >> $GITHUB_STEP_SUMMARY
   echo "| :--- | :--- | :--- |" >> $GITHUB_STEP_SUMMARY
   echo "| adev build | $(stat -c %s dist/bin/adev/dist/browser/index.html) | ${BUILD_TIME}s |" >> $GITHUB_STEP_SUMMARY
   ```
   Contributors and maintainers see bundle sizes immediately on the GitHub Actions run summary page with zero external dependencies.

---

### Option B: Google Cloud Platform "Always Free" Tier ($0/year)

If your enterprise or customer specifically requires **BigQuery SQL analytics** and Looker Studio dashboard connectivity:

1. **GCP Always Free Allowance**:
   Google Cloud provides a permanent free tier for BigQuery:
   * **10 GiB active storage per month** (Free).
   * **1 TiB query data scanned per month** (Free).
2. **Usage Calculation for a Forked Repository**:
   * A maintenance fork executing ~20–50 builds/month produces **< 20 MiB of performance telemetry per year**.
   * Analytical reporting queries consume **< 1 GiB per month**.
   * Total usage consumes **less than 0.2% of the monthly free tier**, resulting in **$0.00 billed cost**.
3. **Setup Steps**:
   * Create a free GCP project (e.g., `fork-angular-ci`).
   * Create a BigQuery dataset (`telemetry`) and table (`perf_benchmarks`).
   * Create a Workload Identity Pool and provider mapped to your repository:
     `assertion.repository == '<your-org>/angular'`
   * Grant the service account the `roles/bigquery.dataEditor` role.
   * Update the 3 strings in `perf.yml` (`project_id`, `workload_identity_provider`, `service_account`).

---

## 7. Comparison Matrix: Upstream vs. Forked Options

| Dimension | Upstream Original (`perf.yml`) | Fork Option A: Native Artifacts (Preferred) | Fork Option B: GCP Free Tier |
| :--- | :--- | :--- | :--- |
| **Annual Infra Cost** | **$120 – $360 / year** | **$0.00 / year** | **$0.00 / year** |
| **Compute Engine** | GitHub `ubuntu-latest` (Free OSS) | GitHub `ubuntu-latest` (Free OSS) | GitHub `ubuntu-latest` (Free OSS) |
| **Authentication** | Google Cloud WIF (`internal-200822`) | None (Built-in `GITHUB_TOKEN`) | Customer GCP WIF (Free) |
| **Storage Destination** | Google BigQuery & GCS | GitHub Actions Artifacts / Summaries | Customer BigQuery (Always Free Tier) |
| **External Credentials** | Required (GCP IAM Provider) | None (Zero secrets or cloud accounts) | Required (Customer GCP Project) |
| **Maintenance Effort** | Continuous GCP project governance | Zero maintenance | Occasional GCP IAM review |
| **Suitability for Fork** | Fails with 403 Forbidden | **Recommended baseline for public forks** | Suitable if customer mandates BigQuery |


---

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

