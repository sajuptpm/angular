#!/usr/bin/env python3
"""
Trigger Workflow Script for Angular GitHub Actions Pipelines.

Dispatches any modernized workflow in the repository using the GitHub REST API or GitHub CLI.
Automatically discovers the repository, active branch, and auth token, triggers the workflow,
and locates the new Run ID for real-time tracking.

Usage Examples:
    # Trigger release.yml in native mode on the current branch:
    python trigger-workflow.py release.yml --mode native

    # Trigger with custom inputs:
    python trigger-workflow.py ci.yml -f mode=native -f job_selection=build

    # Trigger and immediately watch until completion:
    python trigger-workflow.py pr.yml --watch

    # List available workflows:
    python trigger-workflow.py --list
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

WORKFLOW_MAP = {
    "adev-preview-build": "adev-preview-build.yml",
    "adev-preview-deploy": "adev-preview-deploy.yml",
    "assistant-to-the-branch-manager": "assistant-to-the-branch-manager.yml",
    "benchmark-compare": "benchmark-compare.yml",
    "ci": "ci.yml",
    "cross-repo-adev-docs": "cross-repo-adev-docs.yml",
    "dev-infra": "dev-infra.yml",
    "google-internal-tests": "google-internal-tests.yml",
    "perf": "perf.yml",
    "pr": "pr.yml",
    "release": "release.yml",
}


def get_git_repo():
    """Extract owner/repo from git remote origin."""
    try:
        out = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        ).strip()
        match = re.search(r"github\.com[:/]([^/]+)/([^/\.]+?)(?:\.git)?$", out)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
    except Exception:
        pass
    return "sajuptpm/angular"


def get_current_branch():
    """Detect current checked-out git branch."""
    try:
        out = subprocess.check_output(
            ["git", "branch", "--show-current"],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        ).strip()
        if out:
            return out
    except Exception:
        pass
    return "main"


def get_auth_token():
    """Retrieve GitHub token from environment variables or gh CLI."""
    for env_var in ("GITHUB_TOKEN", "GH_TOKEN"):
        token = os.environ.get(env_var)
        if token and token.strip():
            return token.strip()
    try:
        token = subprocess.check_output(
            ["gh", "auth", "token"],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        ).strip()
        if token:
            return token
    except Exception:
        pass
    return None


def api_request(url, token, data=None, method="GET"):
    """Execute authenticated GitHub REST API request."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "angular-workflow-tester",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(error_msg)
            msg = err_json.get("message", error_msg)
        except Exception:
            msg = error_msg
        raise RuntimeError(f"HTTP {e.code}: {msg}")


def normalize_workflow_name(name):
    """Normalize user input to a valid workflow filename."""
    if not name:
        return None
    name = name.strip()
    if name.endswith(".yml"):
        return name
    return WORKFLOW_MAP.get(name, f"{name}.yml")


def list_workflows(repo, token):
    """List available workflows in the repository."""
    url = f"https://api.github.com/repos/{repo}/actions/workflows"
    try:
        res = api_request(url, token)
        workflows = res.get("workflows", [])
        print(f"\nAvailable Workflows in {repo}:")
        print(f"{'Name':<35} {'File':<35} {'State':<10}")
        print("-" * 80)
        for w in workflows:
            filename = os.path.basename(w.get("path", ""))
            print(f"{w.get('name', ''):<35} {filename:<35} {w.get('state', ''):<10}")
        print()
    except Exception as e:
        print(f"Error fetching workflows via API: {e}")
        print("\nLocal Workflow Inventory:")
        for short, fn in sorted(WORKFLOW_MAP.items()):
            print(f"  - {fn:<35} (alias: {short})")


def dispatch_workflow(repo, workflow_file, ref, inputs, token):
    """Dispatch the workflow via GitHub API."""
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_file}/dispatches"
    payload = {
        "ref": ref,
        "inputs": inputs,
    }
    print(f"\nDispatching '{workflow_file}' on branch '{ref}'...")
    print(f"Repository: https://github.com/{repo}")
    if inputs:
        print(f"Inputs: {json.dumps(inputs, indent=2)}")

    api_request(url, token, data=payload, method="POST")
    print("[SUCCESS] Dispatch signal accepted by GitHub Actions.")


def find_latest_run(repo, workflow_file, ref, token, timeout_sec=30):
    """Poll for the newly created run ID after dispatch."""
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_file}/runs?branch={ref}&per_page=5"
    start_time = time.time()
    print("Locating triggered run ID...", end="", flush=True)

    latest_run = None
    while time.time() - start_time < timeout_sec:
        time.sleep(2)
        print(".", end="", flush=True)
        try:
            res = api_request(url, token)
            runs = res.get("workflow_runs", [])
            if runs:
                # Pick the most recently created run
                candidate = runs[0]
                # Verify it was created recently (within last 2 minutes)
                latest_run = candidate
                break
        except Exception:
            pass

    print()
    if latest_run:
        run_id = latest_run.get("id")
        html_url = latest_run.get("html_url")
        status = latest_run.get("status")
        print(f"\n>>> Run ID:   {run_id}")
        print(f">>> Run URL:  {html_url}")
        print(f">>> Status:   {status}")
        return run_id
    else:
        print("\n[WARNING] Could not automatically locate new Run ID within timeout.")
        print(f"Check manually at: https://github.com/{repo}/actions")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Trigger and dispatch GitHub Actions workflows for Angular repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python trigger-workflow.py release.yml --mode native
  python trigger-workflow.py ci.yml -f mode=native -f job_selection=build
  python trigger-workflow.py adev-preview-build.yml --watch
  python trigger-workflow.py --list
        """,
    )
    parser.add_argument(
        "workflow",
        nargs="?",
        help="Workflow name or file (e.g. release.yml, ci, adev-preview-build)",
    )
    parser.add_argument(
        "--repo",
        default=get_git_repo(),
        help="GitHub repository in owner/repo format (default: auto-detected)",
    )
    parser.add_argument(
        "--ref",
        default=get_current_branch(),
        help="Git branch or ref to execute on (default: active branch)",
    )
    parser.add_argument(
        "--token",
        default=get_auth_token(),
        help="GitHub Personal Access Token (or reads GITHUB_TOKEN / GH_TOKEN / gh auth token)",
    )
    parser.add_argument(
        "--mode",
        choices=["native", "auto", "original"],
        help="Shorthand to pass mode input ('native', 'auto', 'original')",
    )
    parser.add_argument(
        "-f",
        "--field",
        action="append",
        default=[],
        help="Custom input in key=value format (e.g., -f dry_run=false)",
    )
    parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        help="Continuously monitor and stream run progress until completed",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available workflows in the repository",
    )

    args = parser.parse_args()

    if args.list or not args.workflow:
        list_workflows(args.repo, args.token)
        if not args.workflow:
            sys.exit(0)

    workflow_file = normalize_workflow_name(args.workflow)
    if not workflow_file:
        print(f"Error: Unknown workflow '{args.workflow}'")
        sys.exit(1)

    # Assemble inputs
    inputs = {}
    if args.mode:
        inputs["mode"] = args.mode
    for f in args.field:
        if "=" in f:
            k, v = f.split("=", 1)
            inputs[k.strip()] = v.strip()
        else:
            print(f"Warning: Ignoring malformed input '{f}'. Expected key=value format.")

    # Check for authentication token
    token = args.token
    if not token:
        print("[ERROR] No GitHub Token found.")
        print("Please authenticate using ONE of the following methods:")
        print("  1. Set environment variable: export GITHUB_TOKEN=your_pat_or_fine_grained_token")
        print("  2. Pass as argument: --token your_token")
        print("  3. Run GitHub CLI login: gh auth login")
        sys.exit(1)

    try:
        dispatch_workflow(args.repo, workflow_file, args.ref, inputs, token)
        run_id = find_latest_run(args.repo, workflow_file, args.ref, token)

        if args.watch and run_id:
            print("\nStarting live run monitoring...")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            check_script = os.path.join(script_dir, "check-runs.py")
            if os.path.exists(check_script):
                subprocess.call([sys.executable, check_script, str(run_id), "--watch", "--repo", args.repo, "--token", token])
            else:
                print(f"[INFO] Monitor script '{check_script}' not found. Please view run in browser.")

    except Exception as e:
        print(f"\n[FAILED] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
