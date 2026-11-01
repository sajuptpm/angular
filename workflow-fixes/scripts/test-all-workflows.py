#!/usr/bin/env python3
"""
End-to-End Suite Runner for Angular GitHub Actions Workflows.

Triggers and validates all modernized workflows in sequence or batch, monitoring their progress
and compiling an end-to-end execution summary report.

Usage Examples:
    # Run full sequential verification of all workflows:
    python test-all-workflows.py

    # Run quick smoke test on lightweight workflows only:
    python test-all-workflows.py --quick

    # Run specific workflows:
    python test-all-workflows.py --workflows dev-infra,google-internal-tests,perf
"""

import argparse
import os
import subprocess
import sys
import time

ALL_WORKFLOWS = [
    {
        "file": "assistant-to-the-branch-manager.yml",
        "name": "Assistant to Branch Manager",
        "inputs": {"mode": "native"},
        "quick": True,
    },
    {
        "file": "dev-infra.yml",
        "name": "Dev Infra Triage & Labeling",
        "inputs": {"mode": "native"},
        "quick": True,
    },
    {
        "file": "google-internal-tests.yml",
        "name": "Google Internal Tests Check",
        "inputs": {"mode": "native"},
        "quick": True,
    },
    {
        "file": "cross-repo-adev-docs.yml",
        "name": "Cross-Repo Docs Sync",
        "inputs": {"mode": "native"},
        "quick": True,
    },
    {
        "file": "adev-preview-deploy.yml",
        "name": "adev Docs Preview Deploy",
        "inputs": {"mode": "native"},
        "quick": True,
    },
    {
        "file": "pr.yml",
        "name": "PR Validation Suite",
        "inputs": {"mode": "native", "job_selection": "lint"},
        "quick": True,
    },
    {
        "file": "benchmark-compare.yml",
        "name": "Benchmark Compare Suite",
        "inputs": {"mode": "native"},
        "quick": False,
    },
    {
        "file": "ci.yml",
        "name": "Continuous Integration",
        "inputs": {"mode": "native", "job_selection": "build"},
        "quick": False,
    },
    {
        "file": "perf.yml",
        "name": "Performance Benchmarks",
        "inputs": {"mode": "native"},
        "quick": False,
    },
    {
        "file": "release.yml",
        "name": "Publish Release Packages",
        "inputs": {"mode": "native", "dry_run": "true"},
        "quick": False,
    },
    {
        "file": "adev-preview-build.yml",
        "name": "adev Docs Preview Build",
        "inputs": {"mode": "native"},
        "quick": False,
    },
]


def run_cmd(cmd):
    """Execute command and capture output."""
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return res.returncode, res.stdout, res.stderr


def main():
    parser = argparse.ArgumentParser(
        description="Sequential end-to-end suite runner for all Angular workflows.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only lightweight workflows (under 1 minute execution)",
    )
    parser.add_argument(
        "--workflows",
        help="Comma-separated list of workflow filenames to run",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Dispatch all workflows without waiting for each to complete",
    )

    args = parser.parse_args()

    # Determine workflows to execute
    if args.workflows:
        targets = [w.strip() for w in args.workflows.split(",")]
        selected = [item for item in ALL_WORKFLOWS if item["file"] in targets or item["file"].replace(".yml", "") in targets]
    elif args.quick:
        selected = [item for item in ALL_WORKFLOWS if item.get("quick")]
    else:
        selected = ALL_WORKFLOWS

    script_dir = os.path.dirname(os.path.abspath(__file__))
    trigger_script = os.path.join(script_dir, "trigger-workflow.py")

    print("\n" + "=" * 80)
    print("ANGULAR WORKFLOW SUITE EXECUTION")
    print(f"Total workflows selected: {len(selected)}")
    print("=" * 80 + "\n")

    results = []

    for idx, item in enumerate(selected, 1):
        wf_file = item["file"]
        wf_name = item["name"]
        wf_inputs = item.get("inputs", {})

        print(f"\n[{idx}/{len(selected)}] Starting '{wf_name}' ({wf_file})...")

        cmd = [sys.executable, trigger_script, wf_file]
        for k, v in wf_inputs.items():
            cmd.extend(["-f", f"{k}={v}"])

        if not args.no_wait:
            cmd.append("--watch")

        t0 = time.time()
        ret, stdout, stderr = run_cmd(cmd)
        dur = int(time.time() - t0)

        status_str = "SUCCESS" if ret == 0 else "FAILED"
        print(f"Result: {status_str} (Duration: {dur}s)")
        if ret != 0:
            print(f"Error Output:\n{stderr or stdout}")

        results.append({
            "name": wf_name,
            "file": wf_file,
            "status": status_str,
            "duration": dur,
        })

    print("\n" + "=" * 80)
    print("SUITE EXECUTION SUMMARY")
    print("=" * 80)
    print(f"{'Workflow':<32} {'File':<35} {'Result':<10} {'Duration'}")
    print("-" * 80)
    for r in results:
        print(f"{r['name']:<32} {r['file']:<35} {r['status']:<10} {r['duration']}s")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
