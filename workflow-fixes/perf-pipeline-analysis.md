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
