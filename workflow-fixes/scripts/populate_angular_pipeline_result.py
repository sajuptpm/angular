#!/usr/bin/env python3
"""
Populate Column 32 ('Do we need this pipeline in forked repo for enterprise release ? Answer with reason')
in workflow-fixes/angular_pipeline_result.xlsx.
"""

import openpyxl
from openpyxl.styles import Alignment, Border, Font, Side

COL32_DATA = {
    "release.yml": (
        "YES (CRITICAL / MANDATORY). "
        "This is the core pipeline that compiles, packages, and bundles all Angular npm distributions "
        "(@angular/core, @angular/common, @angular/router, etc.) into production release packages. "
        "Without this pipeline, an enterprise cannot produce release-ready npm artifacts, build the "
        "angular-release-packages.tar.gz bundle, or publish releases to an internal package registry "
        "(Artifactory, Nexus, AWS CodeArtifact, or GitHub Packages)."
    ),
    "dev-infra.yml": (
        "NO (OPTIONAL / NOT REQUIRED FOR RELEASE). "
        "This pipeline is solely for repository hygiene, automated issue triage via Gemini AI, and PR label "
        "management in the upstream open-source project. It performs no compilation, packaging, testing, or "
        "release distribution. While helpful for repository automation on active forks, it has zero impact "
        "on compiled release binaries or package integrity."
    ),
    "google-internal-tests.yml": (
        "NO (OPTIONAL / NOT REQUIRED FOR RELEASE). "
        "This pipeline enforces internal Google presubmit testing (Google TAP / Piper sync to Google's internal "
        "google3 codebase) via corporate intranet URLs (http://go/angular-g3sync-start). For an enterprise fork, "
        "internal Google3 sync is irrelevant. The native fallback sets the commit status check to SUCCESS to "
        "satisfy PR merge gates, but the pipeline itself is not required for enterprise releases."
    ),
    "pr.yml": (
        "YES (CRITICAL / MANDATORY QUALITY GATE). "
        "This is the primary continuous integration and verification gate for all incoming pull requests and commits. "
        "It executes linting, commit formatting, circular dependency validation, and package compilation. For an "
        "enterprise release, passing pr.yml guarantees code quality and build integrity before changes are merged "
        "into release branches, preventing regressions in production packages."
    ),
    "assistant-to-the-branch-manager.yml": (
        "NO (OPTIONAL / CONVENIENCE ONLY). "
        "In upstream Angular, this pipeline automates branch cherry-picks into version branches (e.g. 17.1.x) "
        "using Google's Angular Robot GitHub App and dispatches to angular/dev-infra. In an enterprise fork, "
        "branch management is typically handled manually or via standard Git PR workflows. While native mode "
        "sets the mergeability status check, it is not required for building or publishing enterprise releases."
    ),
    "cross-repo-adev-docs.yml": (
        "NO (OPTIONAL / NOT REQUIRED FOR RELEASE). "
        "This pipeline synchronizes documentation markdown files from external Angular repositories (e.g. "
        "angular/cli, angular/components) into the adev/ directory and creates PRs via a bot fork. It has "
        "no role in compiling framework packages, running unit tests, or publishing enterprise releases."
    ),
    "ci.yml": (
        "YES (CRITICAL / MANDATORY). "
        "This is the core post-merge continuous integration pipeline that validates the active branch, compiles "
        "all Angular snapshot packages (angular-snapshot-packages), and builds the production documentation site "
        "(adev-production-site). In an enterprise environment, ci.yml serves as the post-merge verification gate "
        "to ensure the release commit builds cleanly and all packages are intact before triggering release.yml."
    ),
    "adev-preview-build.yml": (
        "NO (OPTIONAL / ONLY IF HOSTING DOCS PREVIEWS). "
        "This workflow compiles the angular.dev documentation site into a preview bundle for active pull requests "
        "so reviewers can visually inspect docs changes. It does not compile or publish the @angular/* framework "
        "packages. For enterprise releases of the Angular framework libraries, this pipeline is not needed unless "
        "the organization specifically maintains and previews a customized internal documentation portal."
    ),
    "adev-preview-deploy.yml": (
        "NO (OPTIONAL / ONLY IF HOSTING DOCS PREVIEWS). "
        "This workflow deploys preview artifacts from adev-preview-build.yml to Google Firebase Hosting and posts "
        "sticky comments on PRs. It has zero involvement in building, testing, or publishing enterprise Angular "
        "framework packages. Unless the enterprise is deploying live PR doc previews to an internal Firebase project, "
        "it can be safely omitted from the release path."
    ),
    "benchmark-compare.yml": (
        "NO (OPTIONAL / ON-DEMAND ONLY). "
        "This workflow is an on-demand performance comparison tool triggered only by issue/PR comments (/run-benchmark) "
        "to compare runtime performance between base and PR branches. It is not part of the standard release gate "
        "and does not generate release artifacts. While valuable for deep performance optimization on complex PRs, "
        "it is completely optional for cutting an enterprise release."
    ),
    "perf.yml": (
        "NO (OPTIONAL / TELEMETRY ONLY). "
        "This workflow measures framework bundle sizes and uploads historical telemetry data to Google Cloud "
        "BigQuery and Cloud Storage via GCP Workload Identity Federation. It is an analytics and regression tracking "
        "tool rather than a release blocker or package generator. For an enterprise release, bundle size tracking "
        "can be monitored locally if desired, but automated cloud telemetry is not required to publish enterprise packages."
    ),
}


def populate_col32(filepath):
    wb = openpyxl.load_workbook(filepath)
    ws = wb["angular"]

    print(f"Loaded '{filepath}', sheet: 'angular' (rows: {ws.max_row}, cols: {ws.max_column})")
    print(f"Col 32 Header: {ws.cell(1, 32).value}")

    font = Font(name="Calibri", size=11, bold=False)
    alignment = Alignment(wrap_text=True, vertical="center")
    thin_border = Border(
        left=Side(style="thin", color="D3D3D3"),
        right=Side(style="thin", color="D3D3D3"),
        top=Side(style="thin", color="D3D3D3"),
        bottom=Side(style="thin", color="D3D3D3"),
    )

    updated = 0
    for r in range(2, ws.max_row + 1):
        yaml_file = ws.cell(r, 3).value
        if yaml_file in COL32_DATA:
            cell = ws.cell(r, 32)
            cell.value = COL32_DATA[yaml_file]
            cell.font = font
            cell.alignment = alignment
            cell.border = thin_border
            updated += 1
            print(f"Populated Row {r} ({yaml_file}): {cell.value[:60]}...")
        else:
            print(f"Warning: Unknown YAML file '{yaml_file}' at row {r}")

    wb.save(filepath)
    print(f"\n[SUCCESS] Successfully populated {updated} rows in '{filepath}'.")


if __name__ == "__main__":
    populate_col32("workflow-fixes/angular_pipeline_result.xlsx")
