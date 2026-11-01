#!/usr/bin/env python3
"""
Check Run Jobs Script for Angular GitHub Actions Pipelines.

Analyzes workflow runs and jobs to provide detailed statistics on:
- Passed, Failed, Running, and Skipped jobs.
- Exact execution duration and queue wait times.
- Granular step-level failure diagnostics and logs.
- Cross-pipeline health overview for all workflows in the repository.

Usage Examples:
    # Deep analysis of a specific run by ID:
    python check-run-jobs.py 41348685585

    # Cross-pipeline dashboard of the latest run for every workflow:
    python check-run-jobs.py --overview

    # Filter runs by status (e.g. find all failed runs):
    python check-run-jobs.py --status failure

    # Filter by specific workflow:
    python check-run-jobs.py --workflow ci.yml

    # Export output as GitHub Markdown table:
    python check-run-jobs.py 41348685585 --markdown
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


def api_request(url, token, method="GET"):
    """Execute authenticated GitHub REST API request."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "angular-check-run-jobs",
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


def parse_iso(ts_str):
    """Parse ISO 8601 timestamp."""
    if not ts_str:
        return None
    return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))


def format_duration(seconds):
    """Format seconds into readable human string."""
    if seconds is None or seconds < 0:
        return "-"
    sec = int(seconds)
    if sec < 60:
        return f"{sec}s"
    m, s = divmod(sec, 60)
    if m < 60:
        return f"{m}m {s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h {m:02d}m {s:02d}s"


def compute_duration(start_str, end_str=None):
    """Compute duration between timestamps."""
    t0 = parse_iso(start_str)
    if not t0:
        return None
    t1 = parse_iso(end_str) if end_str else datetime.now(timezone.utc)
    return (t1 - t0).total_seconds()


def get_run_details(repo, run_id, token):
    """Retrieve run and jobs."""
    run_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}"
    jobs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100"

    run_data = api_request(run_url, token)
    jobs_data = api_request(jobs_url, token)
    return run_data, jobs_data.get("jobs", [])


def analyze_run_jobs(run_data, jobs):
    """Categorize jobs into passed, failed, running, skipped and compute metrics."""
    passed = []
    failed = []
    running = []
    skipped = []

    total_job_execution_seconds = 0.0

    for j in jobs:
        status = j.get("status")
        conclusion = j.get("conclusion")

        dur = compute_duration(j.get("started_at"), j.get("completed_at"))
        if dur:
            total_job_execution_seconds += dur

        j_info = {
            "id": j.get("id"),
            "name": j.get("name"),
            "status": status,
            "conclusion": conclusion or "in_progress",
            "started_at": j.get("started_at"),
            "completed_at": j.get("completed_at"),
            "duration": dur,
            "runner": ",".join(j.get("labels", [])) or "default",
            "steps": j.get("steps", []),
            "html_url": j.get("html_url"),
        }

        if status == "completed":
            if conclusion == "success":
                passed.append(j_info)
            elif conclusion == "skipped":
                skipped.append(j_info)
            else:
                failed.append(j_info)
        elif status in ("in_progress", "queued"):
            running.append(j_info)
        else:
            failed.append(j_info)

    # Queue wait time (created_at to run_started_at)
    created_at = parse_iso(run_data.get("created_at"))
    started_at = parse_iso(run_data.get("run_started_at"))
    completed_at = parse_iso(run_data.get("updated_at")) if run_data.get("status") == "completed" else None

    queue_wait_sec = (started_at - created_at).total_seconds() if (started_at and created_at) else None
    pipeline_duration_sec = (completed_at - started_at).total_seconds() if (completed_at and started_at) else compute_duration(run_data.get("run_started_at"))

    return {
        "passed": passed,
        "failed": failed,
        "running": running,
        "skipped": skipped,
        "total_jobs": len(jobs),
        "queue_wait_sec": queue_wait_sec,
        "pipeline_duration_sec": pipeline_duration_sec,
        "total_job_execution_seconds": total_job_execution_seconds,
    }


def print_single_run_report(run_data, jobs, markdown=False):
    """Display comprehensive job breakdown for a single run."""
    stats = analyze_run_jobs(run_data, jobs)

    run_id = run_data.get("id")
    name = run_data.get("name")
    status = run_data.get("status", "").upper()
    conclusion = (run_data.get("conclusion") or "IN PROGRESS").upper()
    branch = run_data.get("head_branch")
    sha = run_data.get("head_sha", "")[:10]
    event = run_data.get("event")
    url = run_data.get("html_url")

    if markdown:
        print(f"### Pipeline Job Analysis: {name} (Run #{run_id})\n")
        print(f"- **Status / Conclusion**: `{status}` / `{conclusion}`")
        print(f"- **Branch / Commit**: `{branch}` (`{sha}`) via `{event}`")
        print(f"- **Total Pipeline Duration**: `{format_duration(stats['pipeline_duration_sec'])}`")
        print(f"- **Queue Wait Time**: `{format_duration(stats['queue_wait_sec'])}`")
        print(f"- **Job Stats**: Passed: `{len(stats['passed'])}` | Failed: `{len(stats['failed'])}` | Running: `{len(stats['running'])}` | Skipped: `{len(stats['skipped'])}`\n")

        print("| Job Name | Status | Conclusion | Duration | Runner | URL |")
        print("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for j in jobs:
            dur = format_duration(compute_duration(j.get("started_at"), j.get("completed_at")))
            conc = j.get("conclusion") or j.get("status")
            runner = ",".join(j.get("labels", [])) or "default"
            print(f"| {j.get('name')} | {j.get('status')} | {conc} | {dur} | {runner} | [View Job]({j.get('html_url')}) |")
        return

    # Terminal ASCII Print
    print("\n" + "=" * 85)
    print(f"PIPELINE RUN #{run_id} : {name}")
    print("=" * 85)
    print(f"Status:       {status} | Conclusion: {conclusion}")
    print(f"Branch:       {branch} (commit: {sha}) | Event: {event}")
    print(f"URL:          {url}")
    print(f"Timing:       Pipeline Elapsed: {format_duration(stats['pipeline_duration_sec'])} | Queue Wait: {format_duration(stats['queue_wait_sec'])}")
    print("-" * 85)
    print(f"JOB SUMMARY:  Total: {stats['total_jobs']}  |  Passed: {len(stats['passed'])}  |  Failed: {len(stats['failed'])}  |  Running: {len(stats['running'])}  |  Skipped: {len(stats['skipped'])}")
    print("-" * 85)

    header = f"{'Job Name':<38} {'Status':<12} {'Conclusion':<12} {'Duration':<10} {'Runner'}"
    print(header)
    print("-" * 85)

    for j in jobs:
        j_name = j.get("name", "")[:36]
        j_status = j.get("status", "")
        j_conc = j.get("conclusion") or "in_progress"
        dur = format_duration(compute_duration(j.get("started_at"), j.get("completed_at")))
        runner = ",".join(j.get("labels", []))[:15] or "default"
        print(f"{j_name:<38} {j_status:<12} {j_conc:<12} {dur:<10} {runner}")

    # Detail failed jobs and steps
    if stats["failed"]:
        print("\n" + "!" * 85)
        print("FAILED JOBS & STEPS DIAGNOSTICS:")
        print("!" * 85)
        for fj in stats["failed"]:
            print(f"\n[JOB FAILED] {fj['name']} (ID: {fj['id']})")
            print(f"  URL: {fj['html_url']}")
            failed_steps = [s for s in fj["steps"] if (s.get("conclusion") or s.get("status")) == "failure"]
            if failed_steps:
                for fs in failed_steps:
                    step_dur = format_duration(compute_duration(fs.get("started_at"), fs.get("completed_at")))
                    print(f"    -> Step: '{fs.get('name')}' (Step #{fs.get('number')}, Duration: {step_dur})")
            else:
                print("    -> No individual step recorded failure (Job may have timed out or failed in runner setup)")

    # Detail running jobs and active steps
    if stats["running"]:
        print("\n" + "~" * 85)
        print("CURRENTLY ACTIVE JOBS:")
        print("~" * 85)
        for rj in stats["running"]:
            elapsed = format_duration(compute_duration(rj["started_at"]))
            print(f"[*] {rj['name']} (Running for {elapsed})")
            active_steps = [s for s in rj["steps"] if s.get("status") == "in_progress"]
            for as_step in active_steps:
                print(f"    -> Executing Step: '{as_step.get('name')}'")

    print("=" * 85 + "\n")


def print_cross_pipeline_overview(repo, token, markdown=False):
    """Scan the latest run for all workflows in the repository and print cross-pipeline dashboard."""
    print(f"\nFetching cross-pipeline health overview for '{repo}'...")
    wf_url = f"https://api.github.com/repos/{repo}/actions/workflows"
    wf_res = api_request(wf_url, token)
    workflows = wf_res.get("workflows", [])

    overview = []
    total_passed_pipelines = 0
    total_failed_pipelines = 0
    total_running_pipelines = 0

    for w in sorted(workflows, key=lambda x: x.get("name", "")):
        wf_id = w.get("id")
        wf_name = w.get("name")
        wf_file = os.path.basename(w.get("path", ""))

        runs_url = f"https://api.github.com/repos/{repo}/actions/workflows/{wf_id}/runs?per_page=1"
        try:
            r_res = api_request(runs_url, token)
            runs = r_res.get("workflow_runs", [])
            if runs:
                latest = runs[0]
                run_id = latest.get("id")
                jobs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100"
                jobs_res = api_request(jobs_url, token)
                jobs = jobs_res.get("jobs", [])
                stats = analyze_run_jobs(latest, jobs)

                conclusion = latest.get("conclusion") or latest.get("status")
                if conclusion == "success":
                    total_passed_pipelines += 1
                elif conclusion in ("failure", "timed_out"):
                    total_failed_pipelines += 1
                elif latest.get("status") in ("in_progress", "queued"):
                    total_running_pipelines += 1

                overview.append({
                    "name": wf_name,
                    "file": wf_file,
                    "run_id": run_id,
                    "status": latest.get("status"),
                    "conclusion": conclusion,
                    "branch": latest.get("head_branch"),
                    "duration": format_duration(stats["pipeline_duration_sec"]),
                    "passed": len(stats["passed"]),
                    "failed": len(stats["failed"]),
                    "skipped": len(stats["skipped"]),
                    "total": stats["total_jobs"],
                    "url": latest.get("html_url"),
                })
        except Exception as e:
            pass

    if markdown:
        print("### Cross-Pipeline Workflow Health Overview\n")
        print(f"**Total Pipelines Analyzed**: `{len(overview)}` | **Passed**: `{total_passed_pipelines}` | **Failed**: `{total_failed_pipelines}` | **Active**: `{total_running_pipelines}`\n")
        print("| Workflow Name | File | Latest Run ID | Outcome | Passed / Total | Skipped | Duration | URL |")
        print("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for item in overview:
            outcome = item['conclusion'].upper()
            jobs_ratio = f"{item['passed']}/{item['total']}"
            print(f"| {item['name']} | `{item['file']}` | [{item['run_id']}]({item['url']}) | `{outcome}` | {jobs_ratio} | {item['skipped']} | {item['duration']} | [Run Link]({item['url']}) |")
        print()
        return

    print("\n" + "=" * 105)
    print(f"CROSS-PIPELINE HEALTH DASHBOARD : {repo}")
    print("=" * 105)
    print(f"Total Workflows: {len(overview)}  |  Passed: {total_passed_pipelines}  |  Failed: {total_failed_pipelines}  |  In Progress: {total_running_pipelines}")
    print("-" * 105)

    header = f"{'Workflow Name':<28} {'Workflow File':<32} {'Run ID':<13} {'Outcome':<11} {'Jobs':<10} {'Duration'}"
    print(header)
    print("-" * 105)

    for item in overview:
        name = item["name"][:26]
        file_name = item["file"][:30]
        run_id_str = str(item["run_id"])
        outcome = item["conclusion"].upper()
        jobs_str = f"{item['passed']}/{item['total']}" + (f" ({item['skipped']} skip)" if item['skipped'] else "")
        dur = item["duration"]
        print(f"{name:<28} {file_name:<32} {run_id_str:<13} {outcome:<11} {jobs_str:<10} {dur}")

    print("=" * 105 + "\n")


def filter_runs_by_status(repo, token, status_filter, limit=20):
    """Find and list runs matching a status (success, failure, in_progress, queued)."""
    print(f"\nSearching runs with status/conclusion = '{status_filter}' on '{repo}'...")
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page={limit}"
    res = api_request(url, token)
    runs = res.get("workflow_runs", [])

    matched = []
    for r in runs:
        status = r.get("status", "")
        conclusion = r.get("conclusion") or ""
        if status_filter.lower() in (status.lower(), conclusion.lower()):
            matched.append(r)

    print(f"Found {len(matched)} matching run(s):\n")
    header = f"{'Run ID':<13} {'Workflow Name':<30} {'Status':<12} {'Conclusion':<12} {'Created At'}"
    print(header)
    print("-" * len(header))
    for m in matched:
        print(f"{m.get('id'):<13} {m.get('name', '')[:28]:<30} {m.get('status'):<12} {str(m.get('conclusion')):<12} {m.get('created_at', '')[:19]}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive analysis of pipeline runs, jobs, statuses, timings, and failures.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python check-run-jobs.py 41348685585
  python check-run-jobs.py --overview
  python check-run-jobs.py --status failure
  python check-run-jobs.py --workflow release.yml
  python check-run-jobs.py 41348685585 --markdown
        """,
    )
    parser.add_argument(
        "run_id",
        nargs="?",
        help="Specific GitHub Actions Run ID to analyze jobs and steps",
    )
    parser.add_argument(
        "--repo",
        default=get_git_repo(),
        help="GitHub repository in owner/repo format (default: auto-detected)",
    )
    parser.add_argument(
        "--token",
        default=get_auth_token(),
        help="GitHub Auth Token (or reads GITHUB_TOKEN / GH_TOKEN / gh auth token)",
    )
    parser.add_argument(
        "--overview",
        action="store_true",
        help="Display cross-pipeline dashboard across the latest runs of ALL workflows",
    )
    parser.add_argument(
        "--status",
        choices=["success", "failure", "in_progress", "queued", "skipped", "cancelled"],
        help="Filter recent runs by status or conclusion",
    )
    parser.add_argument(
        "--workflow",
        help="Filter by specific workflow filename (e.g., release.yml, ci.yml)",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Format output as GitHub Markdown table",
    )

    args = parser.parse_args()

    token = args.token

    if args.overview:
        print_cross_pipeline_overview(args.repo, token, markdown=args.markdown)
        sys.exit(0)

    if args.status:
        filter_runs_by_status(args.repo, token, args.status)
        sys.exit(0)

    if args.workflow and not args.run_id:
        url = f"https://api.github.com/repos/{args.repo}/actions/workflows/{args.workflow}/runs?per_page=5"
        res = api_request(url, token)
        runs = res.get("workflow_runs", [])
        if not runs:
            print(f"No runs found for workflow '{args.workflow}'.")
            sys.exit(0)
        print(f"\nRecent Runs for '{args.workflow}':")
        for r in runs:
            conc = r.get("conclusion") or r.get("status")
            dur = format_duration(compute_duration(r.get("run_started_at"), r.get("updated_at") if r.get("status") == "completed" else None))
            print(f"  Run #{r.get('id')} : {conc.upper()} ({dur}) - {r.get('created_at', '')[:19]}")
        # Default to inspecting latest run
        args.run_id = str(runs[0].get("id"))
        print(f"\nAnalyzing latest Run #{args.run_id}...\n")

    if not args.run_id:
        # If no arguments provided, default to cross-pipeline overview!
        print_cross_pipeline_overview(args.repo, token, markdown=args.markdown)
        sys.exit(0)

    try:
        run_data, jobs = get_run_details(args.repo, args.run_id, token)
        print_single_run_report(run_data, jobs, markdown=args.markdown)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
