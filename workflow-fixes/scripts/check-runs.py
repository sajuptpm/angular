#!/usr/bin/env python3
"""
Check Runs Script for Angular GitHub Actions Pipelines.

Monitors, inspects, and tracks GitHub Actions workflow runs, jobs, steps, and artifacts.
Uses the GitHub REST API with zero external dependencies (pure Python standard library).

Usage Examples:
    # List recent runs across all workflows:
    python check-runs.py --list

    # List recent runs for a specific workflow:
    python check-runs.py --workflow release.yml

    # Inspect a specific run by ID:
    python check-runs.py 41348685585

    # Continuously watch a run in real time until completion:
    python check-runs.py 41348685585 --watch

    # Download all artifacts produced by a run:
    python check-runs.py 41348685585 --download
"""

import argparse
from datetime import datetime, timezone
import json
import os
import re
import subprocess
import sys
import time
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


def api_request(url, token, method="GET", stream=False):
    """Execute authenticated GitHub REST API request."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "angular-run-monitor",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        if stream:
            return resp
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


def format_duration(start_str, end_str=None):
    """Calculate human-readable duration from ISO timestamps."""
    if not start_str:
        return "-"
    try:
        t0 = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        if end_str:
            t1 = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        else:
            t1 = datetime.now(timezone.utc)
        sec = int((t1 - t0).total_seconds())
        if sec < 60:
            return f"{sec}s"
        m, s = divmod(sec, 60)
        return f"{m}m {s}s"
    except Exception:
        return "-"


def format_bytes(num_bytes):
    """Format bytes into KB / MB."""
    if not num_bytes:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} TB"


def list_recent_runs(repo, token, workflow=None, limit=10):
    """List recent runs in the repository."""
    if workflow:
        url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs?per_page={limit}"
    else:
        url = f"https://api.github.com/repos/{repo}/actions/runs?per_page={limit}"

    res = api_request(url, token)
    runs = res.get("workflow_runs", [])

    print(f"\nRecent Workflow Runs for {repo}:")
    header = f"{'Run ID':<13} {'Workflow':<28} {'Branch':<15} {'Status':<12} {'Conclusion':<12} {'Duration':<9} {'Created At'}"
    print(header)
    print("-" * len(header))

    for r in runs:
        run_id = str(r.get("id"))
        w_name = r.get("name", "")[:26]
        branch = r.get("head_branch", "")[:13]
        status = r.get("status", "")
        conclusion = r.get("conclusion") or "running"
        duration = format_duration(r.get("run_started_at"), r.get("updated_at") if status == "completed" else None)
        created = r.get("created_at", "")[:19].replace("T", " ")

        print(f"{run_id:<13} {w_name:<28} {branch:<15} {status:<12} {conclusion:<12} {duration:<9} {created}")
    print()


def get_run_details(repo, run_id, token):
    """Retrieve full run metadata, jobs, and artifacts."""
    run_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}"
    jobs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs"
    artifacts_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts"

    run_data = api_request(run_url, token)
    jobs_data = api_request(jobs_url, token)
    artifacts_data = api_request(artifacts_url, token)

    return run_data, jobs_data.get("jobs", []), artifacts_data.get("artifacts", [])


def print_run_summary(run_data, jobs, artifacts):
    """Print structured summary of run, jobs, and artifacts."""
    run_id = run_data.get("id")
    name = run_data.get("name")
    status = run_data.get("status")
    conclusion = run_data.get("conclusion") or "in progress"
    branch = run_data.get("head_branch")
    sha = run_data.get("head_sha", "")[:10]
    event = run_data.get("event")
    url = run_data.get("html_url")
    duration = format_duration(run_data.get("run_started_at"), run_data.get("updated_at") if status == "completed" else None)

    print("\n" + "=" * 80)
    print(f"RUN #{run_id} : {name}")
    print("=" * 80)
    print(f"Status:     {status.upper()} | Conclusion: {conclusion.upper()} | Duration: {duration}")
    print(f"Branch:     {branch} (commit: {sha}) | Trigger: {event}")
    print(f"URL:        {url}")
    print("\nJOBS:")
    print(f"{'Job Name':<35} {'Status':<12} {'Conclusion':<12} {'Duration':<10} {'Runner'}")
    print("-" * 80)

    for j in jobs:
        j_name = j.get("name", "")[:33]
        j_status = j.get("status", "")
        j_conclusion = j.get("conclusion") or "running"
        j_dur = format_duration(j.get("started_at"), j.get("completed_at"))
        labels = ",".join(j.get("labels", []))[:15] or "default"
        print(f"{j_name:<35} {j_status:<12} {j_conclusion:<12} {j_dur:<10} {labels}")

        # Show failed or in-progress steps
        if j_conclusion == "failure" or j_status == "in_progress":
            for step in j.get("steps", []):
                step_conc = step.get("conclusion") or step.get("status")
                if step_conc in ("failure", "in_progress"):
                    print(f"   -> Step '{step.get('name')}': {step_conc.upper()}")

    print("\nARTIFACTS:")
    if artifacts:
        print(f"{'Artifact Name':<35} {'Size':<12} {'Expired':<10} {'ID'}")
        print("-" * 80)
        for a in artifacts:
            a_name = a.get("name")
            a_size = format_bytes(a.get("size_in_bytes", 0))
            a_exp = "Yes" if a.get("expired") else "No"
            a_id = str(a.get("id"))
            print(f"{a_name:<35} {a_size:<12} {a_exp:<10} {a_id}")
    else:
        print("  (None generated)")
    print("=" * 80 + "\n")


def watch_run(repo, run_id, token, poll_interval=5):
    """Continuously poll a run until completion."""
    print(f"\nMonitoring Run #{run_id} on {repo} (polling every {poll_interval}s)...")
    last_status = None
    start_time = time.time()

    while True:
        try:
            run_data, jobs, artifacts = get_run_details(repo, run_id, token)
            status = run_data.get("status")
            conclusion = run_data.get("conclusion") or "in progress"
            elapsed = int(time.time() - start_time)

            in_progress_jobs = [j.get("name") for j in jobs if j.get("status") == "in_progress"]
            active_info = f" | Active: {', '.join(in_progress_jobs)}" if in_progress_jobs else ""

            msg = f"[{elapsed}s] Status: {status.upper()} ({conclusion.upper()}){active_info}"
            print(msg)

            if status == "completed":
                print("\n[FINISHED] Run reached terminal state.")
                print_run_summary(run_data, jobs, artifacts)
                return conclusion == "success"

        except Exception as e:
            print(f"[Warning] Polling error: {e}")

        time.sleep(poll_interval)


def download_artifacts(repo, run_id, token, out_dir=None):
    """Download artifacts for a run."""
    if not out_dir:
        out_dir = os.path.join("downloads", str(run_id))
    os.makedirs(out_dir, exist_ok=True)

    _, _, artifacts = get_run_details(repo, run_id, token)
    if not artifacts:
        print(f"No artifacts available for run #{run_id}.")
        return

    print(f"\nDownloading {len(artifacts)} artifact(s) to '{out_dir}'...")
    for a in artifacts:
        name = a.get("name")
        art_id = a.get("id")
        download_url = f"https://api.github.com/repos/{repo}/actions/artifacts/{art_id}/zip"
        dest_file = os.path.join(out_dir, f"{name}.zip")

        print(f"  Fetching '{name}' -> {dest_file}...", end="", flush=True)
        try:
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "angular-artifact-downloader",
            }
            req = urllib.request.Request(download_url, headers=headers)
            with urllib.request.urlopen(req) as resp, open(dest_file, "wb") as f:
                f.write(resp.read())
            print(" [OK]")
        except Exception as e:
            print(f" [FAILED: {e}]")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor, inspect, and check GitHub Actions runs for Angular repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python check-runs.py --list
  python check-runs.py --workflow release.yml
  python check-runs.py 41348685585
  python check-runs.py 41348685585 --watch
  python check-runs.py 41348685585 --download
        """,
    )
    parser.add_argument(
        "run_id",
        nargs="?",
        help="GitHub Actions Run ID to inspect or monitor",
    )
    parser.add_argument(
        "--repo",
        default=get_git_repo(),
        help="GitHub repository in owner/repo format (default: auto-detected)",
    )
    parser.add_argument(
        "--token",
        default=get_auth_token(),
        help="GitHub Personal Access Token (or reads GITHUB_TOKEN / GH_TOKEN / gh auth token)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List recent runs across the repository",
    )
    parser.add_argument(
        "--workflow",
        help="Filter recent runs by workflow filename (e.g. release.yml, ci.yml)",
    )
    parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        help="Watch run progress in real time until completion",
    )
    parser.add_argument(
        "-d",
        "--download",
        action="store_true",
        help="Download artifacts produced by the specified run",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=5,
        help="Seconds between polling intervals when watching (default: 5)",
    )

    args = parser.parse_args()

    token = args.token
    if not token:
        # Some endpoints (like public repo run listing) might work unauthenticated,
        # but rate limits are strict. Inform user.
        print("[NOTICE] Running without GitHub token. Strict API rate limits (60/hr) apply.")

    if args.list or (not args.run_id and not args.workflow):
        list_recent_runs(args.repo, token, workflow=args.workflow)
        sys.exit(0)

    if args.workflow and not args.run_id:
        list_recent_runs(args.repo, token, workflow=args.workflow)
        sys.exit(0)

    if not args.run_id:
        parser.print_help()
        sys.exit(1)

    try:
        run_id = int(args.run_id)
    except ValueError:
        print(f"Error: Invalid Run ID '{args.run_id}'. Expected an integer.")
        sys.exit(1)

    try:
        if args.watch:
            success = watch_run(args.repo, run_id, token, poll_interval=args.poll_interval)
            if args.download:
                download_artifacts(args.repo, run_id, token)
            sys.exit(0 if success else 1)
        else:
            run_data, jobs, artifacts = get_run_details(args.repo, run_id, token)
            print_run_summary(run_data, jobs, artifacts)
            if args.download:
                download_artifacts(args.repo, run_id, token)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
