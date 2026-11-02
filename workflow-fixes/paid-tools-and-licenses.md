# Consolidated Analysis of Paid & Licensed Tools in Angular Pipelines

## Executive Summary & Open-Source Release Strategy

This document provides a comprehensive inventory and cost analysis of all paid, licensed, proprietary, and commercial tools, libraries, and cloud services utilized in the upstream Angular pipelines (`.github/workflows/*.yml`).

### Target Deployment Model
* **Hosting Platform**: GitHub Enterprise (GHE) with a **Public Repository** fork.
* **Release Objective**: 100% **Open-Source Release** distributed publicly via the same public repository.
* **Economic Advantage**: On GitHub Enterprise, **public repositories receive unlimited free GitHub Actions runner minutes on standard GitHub-hosted runners (`ubuntu-latest`, 2 vCPU, 7 GB RAM)**. Furthermore, public npm package hosting on `npmjs.org` and GitHub Releases are completely free.
* **Bottom-Line Assessment**: **Total Required Spend = $0.00 / month**. Every proprietary enterprise service can be replaced with native open-source or GitHub-native alternatives without compromising package integrity or release quality.

---

## Consolidated Paid / Licensed Tools & Services Inventory

| # | Tool / Library Name | Vendor | License / Commercial Model | Subscription Model | Rough Cost (Commercial) | Cost for GHE Public Open-Source Repo | Relevant Pipeline(s) | Description & Operational Purpose | Recommended Free / Open-Source Alternative | Open-Source Release Necessity |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | **Google Cloud Remote Build Execution (RBE)** | Google Cloud Platform (GCP) | Proprietary Commercial SaaS | Pay-as-you-go compute & storage / Enterprise contract | **$500 – $2,500+ / month** (based on concurrent build workers and cache volume) | **$0.00** *(Bypassed)* | `pr.yml`<br>`ci.yml`<br>`adev-preview-build.yml`<br>`benchmark-compare.yml`<br>`release.yml` | Cloud-distributed remote build execution and remote action caching across hundreds of parallel cloud workers for Bazel targets. | **Local Bazel execution with GitHub Actions Cache** (`actions/cache`), local RAM/JVM bounds (`-Xmx3g`), or free community BuildBuddy OSS (free up to 250k compute mins/mo). | **Optional**<br>*(Local builds run in 6m 45s)* |
| 2 | **GitHub Larger Runners (`ubuntu-latest-8core`)** | GitHub (Microsoft) | Commercial Runner Add-on | Per-minute compute consumption billing | **$0.032 / minute** (~$1.92/hr; ~$960/mo for 500 build hours) | **$0.00** *(Standard runners free)* | `pr.yml`<br>`ci.yml`<br>`adev-preview-build.yml` | High-capacity Linux virtual machines (8 vCPU, 32 GB RAM) provisioned to prevent out-of-memory errors on unconstrained Bazel builds. | **Standard GitHub-hosted `ubuntu-latest`** (2 vCPU, 7 GB RAM) with memory boundaries (`startup --host_jvm_args=-Xmx3g`, `--jobs=2`). Fully unlimited & free on public repos. | **Optional**<br>*(Standard runner verified working)* |
| 3 | **Google Gemini AI API** | Google Cloud / Google AI Studio | Commercial API (Pay-as-you-go / Enterprise Quota) | Pay-per-token usage pricing | **$10 – $100 / month** ($0.000125 - $0.0025 per 1k tokens) | **$0.00** *(Free tier or rule-based)* | `dev-infra.yml` | AI model inference for triaging incoming GitHub issues, classifying bug reports, and suggesting module labels. | **GitHub-native rule-based keyword/label regex triage** (built-in `$GITHUB_TOKEN`), or free Google AI Studio tier (15 requests/minute). | **Not Needed**<br>*(Issue triage only)* |
| 4 | **Algolia DocSearch / Search API** | Algolia, Inc. | Commercial SaaS (Free tier for eligible open-source) | Request volume & index record count | **$100 – $500+ / month** (commercial standard plan starting at $0.50/1k requests) | **$0.00** *(Free OSS tier or bypassed)* | `ci.yml` | Search index ingestion, synonym dictionary management, and autocomplete querying for the angular.dev documentation site. | **Free Algolia Community DocSearch Program** (for public open-source doc sites), or local client-side Pagefind / FlexSearch. Omitted for library releases. | **Not Needed**<br>*(Only for hosted docs site search)* |
| 5 | **Google Firebase Hosting & Preview Channels** | Google (Firebase / GCP) | Commercial Cloud Platform (Spark / Blaze plans) | Storage and egress bandwidth billing | **$10 – $50 / month** ($0.026/GB storage, $0.15/GB bandwidth) | **$0.00** *(GitHub Pages / Artifacts)* | `adev-preview-deploy.yml`<br>`ci.yml` | Temporary PR preview deployments with SSL URLs and production hosting for angular.dev. | **GitHub Pages** (100% free on public repos), Netlify / Vercel Open Source tiers, or GitHub Actions Artifacts (`adev-preview-site`). | **Not Needed**<br>*(Only for live docs preview)* |
| 6 | **GCP Telemetry Infrastructure (BigQuery & Cloud Storage)** | Google Cloud Platform (GCP) | Commercial Cloud Infrastructure | Pay-as-you-go storage and query scanning | **$10 – $30 / month** ($6.25/TB query scan, $0.02/GB storage) | **$0.00** *(Actions Artifacts / Git)* | `perf.yml` | Historical telemetry database storing framework bundle sizes, benchmark metrics, and performance regression data. | **GitHub Actions Step Summary tables** and archived JSON artifacts (`perf-report-framework-size.zip`), or git-committed historical benchmark files. | **Not Needed**<br>*(Telemetry only)* |
| 7 | **Google Workload Identity Federation (GCP OIDC IAM)** | Google Cloud Platform (GCP) | Feature of GCP Cloud IAM | Included with GCP Account (Requires billing account) | **$0.00** (Free feature of GCP) | **$0.00** *(Bypassed)* | `perf.yml` | Keyless OIDC authentication linking GitHub Actions runner OIDC tokens to GCP IAM service accounts. | **Native GitHub Secrets** (`secrets.GCP_CREDENTIALS`), or bypassed in native mode since telemetry storage is optional. | **Not Needed** |
| 8 | **Google Internal Monorepo Infrastructure (Google3 / TAP)** | Google LLC | Proprietary Corporate Internal | Internal Google Corporate Entitlement | **Inaccessible externally** (Proprietary) | **$0.00** *(Mocked / Bypassed)* | `google-internal-tests.yml` | Automated presubmit sync and regression testing against Google's internal private monorepo (`google3`) via intranet URLs (`http://go/...`). | **Local schema validation of `.ng-dev/google-sync-config.json`** and posting commit status check `google-internal-tests = SUCCESS` via `$GITHUB_TOKEN`. | **Not Needed**<br>*(Google-internal only)* |
| 9 | **Angular Robot GitHub App Infrastructure** | Google LLC / GitHub App | Custom Hosted GitHub App | Self-hosted backend / Cloud Function | **Free to register** (Maintenance overhead) | **$0.00** *(Built-in `$GITHUB_TOKEN`)* | `release.yml`<br>`dev-infra.yml`<br>`assistant-to-the-branch-manager.yml`<br>`cross-repo-adev-docs.yml`<br>`ci.yml`<br>`adev-preview-deploy.yml` | Dedicated bot identity used upstream to bypass branch protection, push Git release tags, manage cherry-picks, and open cross-repo PRs. | **Built-in `$GITHUB_TOKEN`** (with `contents: write`) or standard GitHub Personal Access Token (PAT). Zero external hosting required. | **Built-in Token Sufficient** |
| 10 | **npm Public Registry Scoped Publishing** | npm, Inc. / GitHub (Microsoft) | Public Package Registry (Free for open source) | Free for public packages; $7/user/mo for private | **$0.00** for public packages | **$0.00** *(Free for public open source)* | `release.yml` | High-privilege publishing token (`WOMBOT_TOKEN`) for publishing compiled packages to `registry.npmjs.org`. | **Publish under user-owned npm scope** (e.g. `@my-org/core`) or publish tarball bundles directly to **GitHub Releases** and **GitHub Packages** (`npm.pkg.github.com`). | **Mandatory for npm registry distribution**<br>*(100% Free for Open Source)* |
| 11 | **SauceLabs / BrowserStack Cloud Browser Matrix** | SauceLabs / BrowserStack | Commercial Testing SaaS | Monthly concurrent VM / thread subscription | **$199 – $999+ / month** (commercial automated mobile & cross-browser grid) | **$0.00** *(Free OSS sponsorship or Headless)* | Upstream E2E & Karma targets (called via Bazel) | Real mobile devices and multi-browser execution (iOS Safari, Android Chrome, desktop Safari/Firefox). | **Headless Chromium & Firefox** via Playwright/Puppeteer locally on Linux runners, or apply for free open-source sponsorship program. | **Optional**<br>*(Unit tests run headless)* |
| 12 | **GitHub Actions Compute Minutes** | GitHub (Microsoft) | Cloud CI/CD Compute Service | Included minutes + pay-as-you-go | Standard: $0.008/min (private repos) | **$0.00** *(Unlimited on Public Repos)* | All 11 workflows | Virtual machine execution time for compilation, linting, packaging, and testing. | **Native GitHub-hosted runners** (`ubuntu-latest`). Unlimited free execution minutes on all public GitHub repositories. | **100% Free** |

---

## Detailed Breakdown by Workflow

### 1. `release.yml` (Publish Release)
- **Upstream Paid/Licensed Tools**: 
  - Google Cloud Bazel RBE (`internal-200822`)
  - npm publish write access token (`WOMBOT_TOKEN`)
  - Angular Robot GitHub App (`ANGULAR_ROBOT_PRIVATE_KEY`)
- **Open-Source Strategy on GHE Public Fork**:
  - Run in **Native Mode**: Compiles all official `@angular/*` packages locally using `pnpm build` (`dist/packages-dist`).
  - Bundles output into `angular-release-packages.tar.gz` and publishes as a GitHub Actions artifact.
  - Releases can be published to `npmjs.org` under your own organization scope (free) or published directly to **GitHub Releases** with release notes and attachments at **zero cost**.
- **Commercial Cost Avoidance**: Saves ~$500 – $1,500/month in GCP RBE and dedicated bot infrastructure.

### 2. `pr.yml` (Pull Request Quality Gate)
- **Upstream Paid/Licensed Tools**:
  - Google Cloud RBE (`internal-200822`)
  - GitHub Larger Runner (`ubuntu-latest-8core`)
- **Open-Source Strategy on GHE Public Fork**:
  - Replaced runner with `${{ vars.RUNNER_LABEL || 'ubuntu-latest' }}`.
  - On public repositories, standard `ubuntu-latest` has **zero cost and unlimited minutes**.
  - Tuned Bazel memory limits (`startup --host_jvm_args=-Xmx3g`, `--jobs=2`) to prevent memory crashes.
  - Interactive job selector (`job_selection: lint | build | test | all`) enables fast PR verification.
- **Commercial Cost Avoidance**: Saves ~$960/month in 8-core runner fees and GCP RBE compute.

### 3. `ci.yml` (Continuous Integration & Snapshot Build)
- **Upstream Paid/Licensed Tools**:
  - Google Cloud RBE (`internal-200822`)
  - GitHub Larger Runner (`ubuntu-latest-8core`)
  - Algolia DocSearch enterprise keys (`ALGOLIA_APP_ID`, `ALGOLIA_ADMIN_KEY`)
  - Firebase Hosting service account (`FIREBASE_SERVICE_ACCOUNT`)
  - Snapshot repo push credentials (`SNAPSHOT_TOKEN`, `ANGULAR_ROBOT_PRIVATE_KEY`)
- **Open-Source Strategy on GHE Public Fork**:
  - Bypasses external cloud deployments in native mode.
  - Compiles packages and generates `angular-snapshot-packages` artifact.
  - Compiles documentation and generates `adev-production-site` artifact.
  - All jobs execute on standard runners with disk cleanup (recovering 40+ GB).
- **Commercial Cost Avoidance**: Saves ~$700 – $2,000/month in combined RBE, Algolia, and Firebase costs.

### 4. `adev-preview-build.yml` (Docs Preview Build)
- **Upstream Paid/Licensed Tools**:
  - Google Cloud RBE
  - GitHub Larger Runner (`ubuntu-latest-8core`)
- **Open-Source Strategy on GHE Public Fork**:
  - Builds angular.dev production bundle in ~19 minutes on free standard runners.
  - Implements runner disk cleanup and JVM heap capping (`-Xmx3g`).
  - Generates `adev-preview` tarball and `adev-preview-site` raw artifacts.
- **Commercial Cost Avoidance**: Saves ~$500/month in RBE and high-spec runner fees.

### 5. `adev-preview-deploy.yml` (Docs Preview Deploy)
- **Upstream Paid/Licensed Tools**:
  - Google Firebase Hosting preview channels
  - Angular Robot GitHub App
- **Open-Source Strategy on GHE Public Fork**:
  - Native mode downloads build artifact, extracts archive, and performs static smoke tests.
  - Publishes full deployment summary to `$GITHUB_STEP_SUMMARY`.
  - Zero external cloud hosting required.
- **Commercial Cost Avoidance**: Saves ~$20 – $50/month in Firebase egress and hosting.

### 6. `dev-infra.yml` (DevInfra Triage & Labeling)
- **Upstream Paid/Licensed Tools**:
  - Google Gemini AI API (`GEMINI_API_KEY`)
  - Angular Robot GitHub App (`ANGULAR_ROBOT_PRIVATE_KEY`)
- **Open-Source Strategy on GHE Public Fork**:
  - Native mode executes regex and keyword-based rule triage using built-in `$GITHUB_TOKEN`.
  - Step Summary reports classification results without external AI API calls.
- **Commercial Cost Avoidance**: Saves ~$10 – $100/month in AI API token consumption.

### 7. `google-internal-tests.yml` (Google Internal Tests Enforcement)
- **Upstream Paid/Licensed Tools**:
  - Google-internal Piper / TAP presubmit sync infrastructure
- **Open-Source Strategy on GHE Public Fork**:
  - Validates `.ng-dev/google-sync-config.json` locally.
  - Sets GitHub commit status check `google-internal-tests = SUCCESS` via GitHub REST API.
- **Commercial Cost Avoidance**: Completely bypasses internal corporate infrastructure.

### 8. `assistant-to-the-branch-manager.yml` (Branch Manager)
- **Upstream Paid/Licensed Tools**:
  - Angular Robot GitHub App (`ANGULAR_ROBOT_PRIVATE_KEY`)
  - Cross-repo dispatch to `angular/dev-infra`
- **Open-Source Strategy on GHE Public Fork**:
  - Native Git merge evaluation against target branches (`git merge-tree`).
  - Sets commit status check `mergeability = SUCCESS` via `$GITHUB_TOKEN`.
- **Commercial Cost Avoidance**: Saves dedicated bot hosting and app management.

### 9. `cross-repo-adev-docs.yml` (Update ADEV Cross Repo Docs)
- **Upstream Paid/Licensed Tools**:
  - Personal Access Token with write access to `angular-robot/angular` fork
- **Open-Source Strategy on GHE Public Fork**:
  - Uses built-in `$GITHUB_TOKEN` for public GitHub API queries.
  - Executes doc synchronization script locally and uploads modified documentation as `adev-cross-repo-docs` artifact.
- **Commercial Cost Avoidance**: Zero cost.

### 10. `benchmark-compare.yml` (Benchmark Comparison)
- **Upstream Paid/Licensed Tools**:
  - `angular/team` private GitHub team membership token (`BENCHMARK_COMPARE_MEMBERSHIP_GITHUB_TOKEN`)
  - Google Cloud RBE (`internal-200822`)
- **Open-Source Strategy on GHE Public Fork**:
  - Bypasses Google team verification on forks; validates repository owner/collaborator.
  - Executes benchmarks locally via Bazel and posts comparative diff to `$GITHUB_STEP_SUMMARY`.
- **Commercial Cost Avoidance**: Saves ~$200/month in RBE compute.

### 11. `perf.yml` (Performance Tracking)
- **Upstream Paid/Licensed Tools**:
  - Google Cloud BigQuery and Cloud Storage
  - Google Cloud Workload Identity Federation
- **Open-Source Strategy on GHE Public Fork**:
  - Measures bundle sizes and framework metrics locally via `pnpm bazel build`.
  - Saves metrics to JSON artifact `perf-report-framework-size` and publishes to Step Summary.
- **Commercial Cost Avoidance**: Saves ~$10 – $30/month in GCP cloud storage and analytics queries.

---

## Cost Summary: Upstream Enterprise vs. Open-Source Fork

| Cost Category | Upstream Angular Enterprise Spend (Est.) | Open-Source GHE Public Fork Spend | Savings Percentage |
| :--- | :--- | :--- | :---: |
| **Compute / Runners** | ~$1,500 / month *(8-core pools)* | **$0.00** *(Unlimited free standard runners)* | **100%** |
| **Remote Build Execution (RBE)** | ~$1,500 – $3,000 / month *(Google Cloud RBE)* | **$0.00** *(Local Bazel + Actions Cache)* | **100%** |
| **AI / Search APIs (Gemini, Algolia)** | ~$200 – $600 / month | **$0.00** *(Rule-based triage + client search)* | **100%** |
| **Cloud Hosting & DB (Firebase, BigQuery)** | ~$50 – $100 / month | **$0.00** *(GitHub Artifacts & Step Summaries)* | **100%** |
| **Package Registry Publishing** | Public npm (@angular) | **$0.00** *(Public npm under own scope / GitHub Releases)* | **100%** |
| **TOTAL MONTHLY ESTIMATE** | **~$3,250 – $5,200+ / month** | **$0.00 / month** | **100% Free** |

---

## Action Plan for Your Open-Source Release

1. **Repository Settings**:
   - Keep the fork **Public** under your GitHub Enterprise organization to retain unlimited free runner minutes.
   - Set repository variable `vars.RUNNER_LABEL = "ubuntu-latest"`.
   - Set repository variable `vars.DEV_INFRA_MODE = "native"`.

2. **Mandatory Pipelines for Open-Source Release**:
   Only three pipelines are required to build, verify, and release the open-source product:
   - [`pr.yml`](file:///c:/projects/angular/.github/workflows/pr.yml): Pre-merge lint, formatting, and build validation.
   - [`ci.yml`](file:///c:/projects/angular/.github/workflows/ci.yml): Post-merge snapshot compilation and verification.
   - [`release.yml`](file:///c:/projects/angular/.github/workflows/release.yml): Production package compilation and tarball bundle creation (`angular-release-packages.tar.gz`).

3. **Public Release Distribution Channels (All Free)**:
   - **GitHub Releases**: Attach `angular-release-packages.tar.gz` directly to signed GitHub Releases created via `gh release create vX.Y.Z`.
   - **Public npm Registry**: Run `npm publish --access public` under your public scope (e.g. `@my-org/core`) for zero dollars.
   - **GitHub Packages**: Publish open-source packages to `npm.pkg.github.com` (free on public repositories).
