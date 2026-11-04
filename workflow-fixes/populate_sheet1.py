import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.load_workbook('workflow-fixes/infra_tool_estimate.xlsx')
ws = wb['Sheet1']

# Clear existing rows below row 1
for r in range(2, ws.max_row + 1):
    for c in range(1, ws.max_column + 1):
        ws.cell(r, c).value = None

data = [
    # pr.yml
    ['angular', 'pr.yml', 'Validates incoming pull requests with linting, unit tests, integration tests, and compilation checks across the Angular monorepo', 'Test', 'Yes', 'Google Cloud Remote Build Execution (RBE)', 'PAYG GCP Service: ~$500–$2,500/month (~$6K–$30K/year)', 'Not Planning / Replacement'],
    ['angular', 'pr.yml', 'Validates incoming pull requests with linting, unit tests, integration tests, and compilation checks across the Angular monorepo', 'Test', 'Yes', 'GitHub Standard Runners (ubuntu-latest)', 'Free for public repos; ~$0.008/min for private repos (~$24/month)', '$288'],
    ['angular', 'pr.yml', 'Validates incoming pull requests with linting, unit tests, integration tests, and compilation checks across the Angular monorepo', 'Test', 'Yes', 'Open Source Toolchain (Bazel, Node.js, pnpm, TypeScript, Jasmine, Karma, Cypress)', 'Open Source (Free)', '$0'],

    # ci.yml
    ['angular', 'ci.yml', 'Executes post-merge CI verification on main/release branches, builds packages, runs tests, creates snapshot builds, and deploys documentation', 'Build', 'Yes', 'Google Cloud Remote Build Execution (RBE)', 'PAYG GCP Service: ~$500–$2,500/month (~$6K–$30K/year)', 'Not Planning / Replacement'],
    ['angular', 'ci.yml', 'Executes post-merge CI verification on main/release branches, builds packages, runs tests, creates snapshot builds, and deploys documentation', 'Build', 'Yes', 'GitHub Larger Runners (ubuntu-latest-8core)', 'PAYG GitHub Runners: ~$0.032/min (50 runs/month × 30 min ≈ $48/month)', '$576'],
    ['angular', 'ci.yml', 'Executes post-merge CI verification on main/release branches, builds packages, runs tests, creates snapshot builds, and deploys documentation', 'Build', 'Yes', 'GitHub Standard Runners (ubuntu-latest)', 'Free for public repos; ~$0.008/min for private repos', 'Included in standard runner pool'],
    ['angular', 'ci.yml', 'Executes post-merge CI verification on main/release branches, builds packages, runs tests, creates snapshot builds, and deploys documentation', 'Release Doc', 'No', 'Google Firebase Hosting & Preview Channels', 'Storage & Bandwidth Billing: ~$10–$50/month (~$120–$600/year)', '$120'],
    ['angular', 'ci.yml', 'Executes post-merge CI verification on main/release branches, builds packages, runs tests, creates snapshot builds, and deploys documentation', 'Release Doc', 'No', 'Algolia DocSearch / Search API', 'Commercial Tier ~$100–$500/month (Free OSS tier available)', 'Not Planning / Replacement'],
    ['angular', 'ci.yml', 'Executes post-merge CI verification on main/release branches, builds packages, runs tests, creates snapshot builds, and deploys documentation', 'Package', 'Yes', 'Open Source Toolchain (Bazel, Node.js, pnpm, Rollup, Terser, TypeScript)', 'Open Source (Free)', '$0'],

    # release.yml
    ['angular', 'release.yml', 'Compiles, validates, and publishes production @angular/* release packages, npm provenance, and tags', 'Release', 'Yes', 'GitHub Standard Runners (ubuntu-latest)', 'Free for public repos; ~$0.008/min for private repos', 'Included in standard runner pool'],
    ['angular', 'release.yml', 'Compiles, validates, and publishes production @angular/* release packages, npm provenance, and tags', 'Package', 'Yes', 'npm Public Registry Scoped Publishing', 'Public OSS Publishing = Free', '$0'],
    ['angular', 'release.yml', 'Compiles, validates, and publishes production @angular/* release packages, npm provenance, and tags', 'Release', 'Yes', 'Angular Robot GitHub App (ANGULAR_ROBOT_PRIVATE_KEY)', 'GitHub App + Cloud Function host: ~$10–$25/month (Free on GitHub native)', '$0'],
    ['angular', 'release.yml', 'Compiles, validates, and publishes production @angular/* release packages, npm provenance, and tags', 'Build', 'Yes', 'Open Source Toolchain (Bazel, Node.js, pnpm, Rollup, Terser)', 'Open Source (Free)', '$0'],

    # adev-preview-build.yml
    ['angular', 'adev-preview-build.yml', 'Compiles and packages angular.dev documentation site for pull request preview deployment when labeled', 'Release Doc', 'No', 'GitHub Larger Runners (ubuntu-latest-8core)', 'PAYG GitHub Runners: ~$0.032/min (~$48/month)', 'Included in Larger Runner line ($576)'],
    ['angular', 'adev-preview-build.yml', 'Compiles and packages angular.dev documentation site for pull request preview deployment when labeled', 'Release Doc', 'No', 'Google Cloud Remote Build Execution (RBE)', 'PAYG GCP Service: ~$500–$2,500/month (~$6K–$30K/year)', 'Not Planning / Replacement'],
    ['angular', 'adev-preview-build.yml', 'Compiles and packages angular.dev documentation site for pull request preview deployment when labeled', 'Release Doc', 'No', 'Open Source Toolchain (Bazel, Node.js, pnpm)', 'Open Source (Free)', '$0'],

    # adev-preview-deploy.yml
    ['angular', 'adev-preview-deploy.yml', 'Deploys compiled documentation preview bundle to Google Firebase Hosting preview channels', 'Release Doc', 'No', 'Google Firebase Hosting & Preview Channels (ng-dev-previews)', 'Storage & Bandwidth Billing: ~$10–$50/month (~$120–$600/year)', 'Included in Firebase Hosting line ($120)'],
    ['angular', 'adev-preview-deploy.yml', 'Deploys compiled documentation preview bundle to Google Firebase Hosting preview channels', 'Release Doc', 'No', 'GitHub Standard Runners (ubuntu-latest)', 'Free for public repos; ~$0.008/min for private repos', 'Included in standard runner pool'],

    # perf.yml
    ['angular', 'perf.yml', 'Measures framework bundle size, runs benchmarks, and tracks telemetry regressions across commits', 'Test', 'No', 'GCP Telemetry (BigQuery & Cloud Storage)', 'PAYG Storage & Queries: ~$10–$30/month (~$120–$360/year)', 'Not Planning / Replacement'],
    ['angular', 'perf.yml', 'Measures framework bundle size, runs benchmarks, and tracks telemetry regressions across commits', 'Test', 'No', 'Google Cloud Workload Identity Federation (WIF)', 'Feature of GCP Cloud IAM: $0', '$0'],
    ['angular', 'perf.yml', 'Measures framework bundle size, runs benchmarks, and tracks telemetry regressions across commits', 'Test', 'No', 'GitHub Standard Runners (ubuntu-latest)', 'Free for public repos; ~$0.008/min for private repos', 'Included in standard runner pool'],

    # dev-infra.yml
    ['angular', 'dev-infra.yml', 'Automates issue classification, PR label assignment, and review change tracking via Angular dev-infra bots', 'Utility', 'No', 'Google Gemini AI API (GOOGLE_GENERATIVE_AI_KEY)', 'PAYG API: ~$10–$100/month ($0.000125–$0.0025/1k tokens)', 'Not Planning / Replacement'],
    ['angular', 'dev-infra.yml', 'Automates issue classification, PR label assignment, and review change tracking via Angular dev-infra bots', 'Utility', 'No', 'Angular Robot GitHub App (ANGULAR_ROBOT_PRIVATE_KEY)', 'GitHub App + Cloud Function host: ~$10–$25/month', '$0'],
    ['angular', 'dev-infra.yml', 'Automates issue classification, PR label assignment, and review change tracking via Angular dev-infra bots', 'Utility', 'No', 'GitHub Standard Runners (ubuntu-latest)', 'Free for public repos; ~$0.008/min for private repos', 'Included in standard runner pool'],

    # assistant-to-the-branch-manager.yml
    ['angular', 'assistant-to-the-branch-manager.yml', 'Validates PR mergeability across release branches, monitors cherry-pick requirements, and sets branch statuses', 'Utility', 'No', 'Angular Robot GitHub App (ANGULAR_ROBOT_PRIVATE_KEY)', 'GitHub App + Cloud Function host: ~$10–$25/month', '$0'],
    ['angular', 'assistant-to-the-branch-manager.yml', 'Validates PR mergeability across release branches, monitors cherry-pick requirements, and sets branch statuses', 'Utility', 'No', 'GitHub Standard Runners (ubuntu-latest)', 'Free for public repos; ~$0.008/min for private repos', 'Included in standard runner pool'],

    # google-internal-tests.yml
    ['angular', 'google-internal-tests.yml', 'Synchronizes changes and triggers presubmit verification against Google internal private monorepo (Google3 / TAP)', 'Internal to Vendor', 'No', 'Google Internal Monorepo Infrastructure (Google3 / TAP)', 'Proprietary Google-internal infrastructure (inaccessible externally)', '$0'],
    ['angular', 'google-internal-tests.yml', 'Synchronizes changes and triggers presubmit verification against Google internal private monorepo (Google3 / TAP)', 'Internal to Vendor', 'No', 'GitHub Standard Runners (ubuntu-latest)', 'Free for public repos; ~$0.008/min for private repos', 'Included in standard runner pool'],

    # benchmark-compare.yml
    ['angular', 'benchmark-compare.yml', 'Compares performance benchmarks on demand between a PR branch and a base commit triggered by PR comments', 'Test', 'No', 'Google Cloud Remote Build Execution (RBE)', 'PAYG GCP Service: ~$500–$2,500/month (~$6K–$30K/year)', 'Not Planning / Replacement'],
    ['angular', 'benchmark-compare.yml', 'Compares performance benchmarks on demand between a PR branch and a base commit triggered by PR comments', 'Test', 'No', 'GitHub Standard Runners (ubuntu-latest)', 'Free for public repos; ~$0.008/min for private repos', 'Included in standard runner pool'],
    ['angular', 'benchmark-compare.yml', 'Compares performance benchmarks on demand between a PR branch and a base commit triggered by PR comments', 'Test', 'No', 'GitHub API Bot Tokens (BENCHMARK_POST_RESULTS_GITHUB_TOKEN)', 'GitHub Personal Access Token / App: Free', '$0'],

    # cross-repo-adev-docs.yml
    ['angular', 'cross-repo-adev-docs.yml', 'Ingests and synchronizes documentation content from external Angular repositories (angular-cli, components)', 'Release Doc', 'No', 'Angular Robot GitHub App / Token (ANGULAR_ROBOT_ACCESS_TOKEN)', 'GitHub Personal Access Token / App: Free', '$0'],
    ['angular', 'cross-repo-adev-docs.yml', 'Ingests and synchronizes documentation content from external Angular repositories (angular-cli, components)', 'Release Doc', 'No', 'GitHub Standard Runners (ubuntu-latest)', 'Free for public repos; ~$0.008/min for private repos', 'Included in standard runner pool'],

    # run-saucelabs-tests.sh
    ['angular', 'run-saucelabs-tests.sh', 'Cross-browser and real-device validation for Angular runtime, Zone.js, DOM events, and browser compatibility', 'Test', 'Yes', 'SauceLabs / BrowserStack Cloud Grid', 'SaaS Subscription: ~$199–$999/month (~$2.4K–$12K/year; targeted: ~$600/year)', '$2,400 (minimum planning)'],
    ['angular', 'run-saucelabs-tests.sh', 'Cross-browser and real-device validation for Angular runtime, Zone.js, DOM events, and browser compatibility', 'Test', 'Yes', 'Open Source Toolchain (Karma, Jasmine, Playwright, Chrome Headless)', 'Open Source (Free)', '$0'],
]

# Header styles
header_font = Font(name='Segoe UI', size=11, bold=True, color='FF000000')
header_fill = PatternFill(start_color='FFF5F5F5', end_color='FFF5F5F5', fill_type='solid')
header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

thin_border = Border(
    left=Side(style='thin', color='FFD9D9D9'),
    right=Side(style='thin', color='FFD9D9D9'),
    top=Side(style='thin', color='FFD9D9D9'),
    bottom=Side(style='thin', color='FFD9D9D9')
)

ws.row_dimensions[1].height = 28
for c in range(1, 9):
    cell = ws.cell(1, c)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_alignment
    cell.border = thin_border

data_font = Font(name='Segoe UI', size=10)
bold_font = Font(name='Segoe UI', size=10, bold=True)
center_align = Alignment(horizontal='center', vertical='top', wrap_text=True)
left_align = Alignment(horizontal='left', vertical='top', wrap_text=True)

for row_idx, row_data in enumerate(data, start=2):
    ws.row_dimensions[row_idx].height = 24
    for col_idx, val in enumerate(row_data, start=1):
        cell = ws.cell(row_idx, col_idx, val)
        cell.font = data_font
        cell.border = thin_border
        if col_idx in [1, 4, 5]:  # Component, Category, Mandatory
            cell.alignment = center_align
            if col_idx == 5:
                cell.font = bold_font
        elif col_idx in [8]:  # Yearly Cost
            cell.alignment = center_align
            cell.font = bold_font
        else:
            cell.alignment = left_align

# Adjust column widths
widths = {1: 14, 2: 28, 3: 45, 4: 18, 5: 14, 6: 35, 7: 42, 8: 26}
for col_idx, width in widths.items():
    ws.column_dimensions[get_column_letter(col_idx)].width = width

wb.save('workflow-fixes/infra_tool_estimate.xlsx')
print(f'Successfully updated Sheet1 with {len(data)} rows.')
