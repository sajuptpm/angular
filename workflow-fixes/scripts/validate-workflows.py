#!/usr/bin/env python3
"""
Workflow Linter & Dual-Mode Compliance Validator for Angular Workflows.

Performs static analysis and compliance validation on all workflow YAML files in
`.github/workflows/*.yml` against the core dual-mode engineering principles:
1. Valid YAML syntax.
2. Presence of `workflow_dispatch` manual trigger with execution mode input.
3. Dynamic, configurable runner labels (`vars.RUNNER_LABEL || 'ubuntu-latest'`).
4. Safe secret handling (NO `secrets.*` inside step `if:` expressions).
5. Modern action dependencies (pinned commits or modern v4 actions).
6. Heavy automatic push trigger guarding to conserve runner minutes.
7. Zero-skipped-jobs dual-mode fallback paths.

Usage Examples:
    # Validate all workflows in the repository:
    python validate-workflows.py

    # Validate a single workflow file:
    python validate-workflows.py release.yml
"""

import argparse
import os
import re
import sys
import yaml


def check_yaml_syntax(filepath):
    """Verify file parses as valid YAML."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return True, data, None
    except Exception as e:
        return False, None, str(e)


def audit_workflow(filepath, data, content):
    """Audit workflow content against dual-mode standards."""
    issues = []
    warnings = []
    passes = []

    filename = os.path.basename(filepath)

    # 1. Check triggers
    raw_on = data.get("on") or data.get(True)  # PyYAML might parse 'on' as boolean True
    has_dispatch = False
    if isinstance(raw_on, dict):
        has_dispatch = "workflow_dispatch" in raw_on
    elif isinstance(raw_on, list):
        has_dispatch = "workflow_dispatch" in raw_on
    elif isinstance(raw_on, str):
        has_dispatch = raw_on == "workflow_dispatch"

    if has_dispatch:
        passes.append("Trigger: 'workflow_dispatch' configured for manual testing")
    else:
        issues.append("Missing 'workflow_dispatch' trigger")

    # 2. Check dynamic runner labels
    jobs = data.get("jobs", {}) if isinstance(data, dict) else {}
    hardcoded_runners = []
    dynamic_runners = []

    for job_id, job_data in jobs.items():
        if not isinstance(job_data, dict):
            continue
        runs_on = str(job_data.get("runs-on", ""))
        if "RUNNER_LABEL" in runs_on:
            dynamic_runners.append(job_id)
        elif runs_on:
            hardcoded_runners.append(f"{job_id} ({runs_on})")

    if dynamic_runners:
        passes.append(f"Runners: {len(dynamic_runners)} job(s) use configurable vars.RUNNER_LABEL")
    if hardcoded_runners:
        warnings.append(f"Hardcoded runner(s) found in jobs: {', '.join(hardcoded_runners)}")

    # 3. Check for secrets inside step `if:` conditions
    # Regex search across steps
    secret_in_if = re.findall(r"if:.*secrets\.\w+", content)
    if secret_in_if:
        issues.append(f"Found forbidden secrets.* reference inside step if: expression: {secret_in_if[0]}")
    else:
        passes.append("Security: Zero secrets.* references inside step if: expressions")

    # 4. Check for heavy un-guarded push triggers
    # Detect active push trigger not commented out
    active_push = re.search(r"^\s*push:\s*$", content, re.MULTILINE)
    if active_push:
        warnings.append("Active push: trigger detected. Ensure runner minutes are monitored.")
    else:
        passes.append("Runner Conservation: Automatic push: trigger safely commented or guarded")

    # 5. Check action versions (detect upload-artifact@v3 or checkout@v3)
    deprecated_actions = re.findall(r"actions/(?:upload-artifact|download-artifact|checkout)@v[1-3]", content)
    if deprecated_actions:
        warnings.append(f"Deprecated action version(s) found: {', '.join(set(deprecated_actions))}. Migrate to v4.")
    else:
        passes.append("Action Pins: Modern action versions / commit SHAs used")

    # 6. Check dual-mode architecture indicator
    if "native" in content and ("original" in content or "auto" in content):
        passes.append("Architecture: Dual-mode resolution ('native' / 'original') present")
    else:
        warnings.append("Dual-mode resolution pattern ('native' / 'original') not detected")

    return {
        "file": filename,
        "valid_yaml": True,
        "passes": passes,
        "warnings": warnings,
        "issues": issues,
        "is_healthy": len(issues) == 0,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Dual-Mode compliance and quality linter for Angular GitHub Actions workflows.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "workflow",
        nargs="?",
        help="Optional specific workflow file to audit (e.g. release.yml)",
    )
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    wf_dir = os.path.join(repo_root, ".github", "workflows")

    if args.workflow:
        target = args.workflow if args.workflow.endswith(".yml") else f"{args.workflow}.yml"
        files = [os.path.join(wf_dir, target)]
    else:
        files = [os.path.join(wf_dir, f) for f in sorted(os.listdir(wf_dir)) if f.endswith(".yml")]

    print("\n" + "=" * 90)
    print("ANGULAR WORKFLOW DUAL-MODE COMPLIANCE & QUALITY AUDIT")
    print(f"Directory: {wf_dir}")
    print(f"Total Workflows Scanned: {len(files)}")
    print("=" * 90 + "\n")

    all_passed = True
    total_issues = 0
    total_warnings = 0

    for fpath in files:
        fname = os.path.basename(fpath)
        if not os.path.exists(fpath):
            print(f"[ERROR] Workflow file '{fpath}' does not exist.")
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        valid, data, err = check_yaml_syntax(fpath)
        if not valid:
            print(f"[FAIL] {fname:<35} : Invalid YAML Syntax ({err})")
            all_passed = False
            total_issues += 1
            continue

        report = audit_workflow(fpath, data, content)

        status_tag = "[PASS]" if report["is_healthy"] else "[FAIL]"
        print(f"{status_tag} {fname:<35} (Checks Passed: {len(report['passes'])}, Warnings: {len(report['warnings'])}, Errors: {len(report['issues'])})")

        for p in report["passes"]:
            print(f"       + {p}")
        for w in report["warnings"]:
            print(f"       ! WARNING: {w}")
            total_warnings += 1
        for i in report["issues"]:
            print(f"       x ERROR: {i}")
            total_issues += 1
            all_passed = False
        print("-" * 90)

    print("\n" + "=" * 90)
    print(f"AUDIT SUMMARY: {'ALL WORKFLOWS COMPLIANT' if all_passed else 'COMPLIANCE ISSUES FOUND'}")
    print(f"Total Errors: {total_issues} | Total Warnings: {total_warnings}")
    print("=" * 90 + "\n")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
