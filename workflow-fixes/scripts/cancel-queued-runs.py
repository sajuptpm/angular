#!/usr/bin/env python3
"""
Cancel Queued / Active Runs Script for Angular GitHub Actions Pipelines.

Lists, inspects, and cancels queued or in-progress workflow runs to conserve
runner minutes and prevent queue congestion.

Usage Examples:
    # List all currently active or queued runs:
    python cancel-queued-runs.py --list

    # Cancel a specific run by ID:
    python cancel-queued-runs.py 41348685585

    # Cancel ALL queued runs:
    python cancel-queued-runs.py --queued

    # Cancel ALL active (queued + in-progress) runs:
    python cancel-queued-runs.py --all
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request


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


def api_request(url, token, method="GET"):
    """Execute authenticated GitHub REST API request."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "angular-cancel-runs",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers, method=method)
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


def list_active_runs(repo, token):
    """Retrieve all queued and in_progress runs."""
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=50"
    res = api_request(url, token)
    runs = res.get("workflow_runs", [])
    active = [r for r in runs if r.get("status") in ("queued", "in_progress")]
    return active


def cancel_run(repo, run_id, token):
    """Cancel a specific workflow run."""
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/cancel"
    try:
        api_request(url, token, method="POST")
        print(f"[SUCCESS] Cancel signal delivered for Run #{run_id}.")
        return True
    except Exception as e:
        print(f"[FAILED] Could not cancel Run #{run_id}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Cancel queued or active GitHub Actions workflow runs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cancel-queued-runs.py --list
  python cancel-queued-runs.py 41348685585
  python cancel-queued-runs.py --queued
  python cancel-queued-runs.py --all
        """,
    )
    parser.add_argument(
        "run_id",
        nargs="?",
        help="Specific Run ID to cancel",
    )
    parser.add_argument(
        "--repo",
        default=get_git_repo(),
        help="GitHub repository in owner/repo format (default: auto-detected)",
    )
    parser.add_argument(
        "--token",
        default=get_auth_token(),
        help="GitHub Auth Token",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all active (queued or in-progress) runs",
    )
    parser.add_argument(
        "--queued",
        action="store_true",
        help="Cancel all currently queued runs",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Cancel ALL active runs (both queued and in-progress)",
    )

    args = parser.parse_args()
    token = args.token

    if not token and (args.run_id or args.queued or args.all):
        print("[ERROR] GitHub token required to cancel workflow runs.")
        print("Please export GITHUB_TOKEN or login via 'gh auth login'.")
        sys.exit(1)

    active_runs = list_active_runs(args.repo, token)

    if args.list or (not args.run_id and not args.queued and not args.all):
        print(f"\nActive Workflow Runs in '{args.repo}':")
        if not active_runs:
            print("  (No queued or in-progress runs found. Runner queue is idle.)\n")
            sys.exit(0)

        header = f"{'Run ID':<13} {'Workflow Name':<30} {'Status':<12} {'Branch':<15} {'Created At'}"
        print(header)
        print("-" * len(header))
        for r in active_runs:
            print(f"{r.get('id'):<13} {r.get('name', '')[:28]:<30} {r.get('status'):<12} {r.get('head_branch', '')[:13]:<15} {r.get('created_at', '')[:19]}")
        print()
        sys.exit(0)

    if args.run_id:
        cancel_run(args.repo, args.run_id, token)
        sys.exit(0)

    if args.queued:
        queued = [r for r in active_runs if r.get("status") == "queued"]
        if not queued:
            print("No queued runs found to cancel.")
            sys.exit(0)
        print(f"Cancelling {len(queued)} queued run(s)...")
        for r in queued:
            cancel_run(args.repo, r.get("id"), token)
        sys.exit(0)

    if args.all:
        if not active_runs:
            print("No active runs found to cancel.")
            sys.exit(0)
        print(f"Cancelling ALL {len(active_runs)} active run(s)...")
        for r in active_runs:
            cancel_run(args.repo, r.get("id"), token)
        sys.exit(0)


if __name__ == "__main__":
    main()
