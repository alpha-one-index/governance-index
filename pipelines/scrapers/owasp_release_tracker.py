#!/usr/bin/env python3
"""OWASP Release Tracker — Monitors OWASP LLM Top 10 and AI security projects.

Unique differentiator: Uses GitHub API to track commits, releases, and issues
on OWASP's official LLM Top 10 repo plus related AI security projects. Detects
new vulnerability entries, severity changes, and mitigation updates in real-time.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "exports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "GovernanceIndex/1.0 (owasp-tracker)",
    "Accept": "application/vnd.github.v3+json",
}

# OWASP repos to monitor
OWASP_REPOS = {
    "llm_top_10": {
        "owner": "OWASP",
        "repo": "www-project-top-10-for-large-language-model-applications",
        "description": "OWASP Top 10 for LLM Applications",
    },
    "ai_security": {
        "owner": "OWASP",
        "repo": "www-project-ai-security-and-privacy-guide",
        "description": "OWASP AI Security and Privacy Guide",
    },
    "ml_top_10": {
        "owner": "OWASP",
        "repo": "www-project-machine-learning-security-top-10",
        "description": "OWASP Machine Learning Security Top 10",
    },
}


def fetch_repo_releases(owner: str, repo: str) -> list:
    """Fetch latest releases from a GitHub repo."""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    try:
        with httpx.Client(timeout=15, headers=HEADERS) as client:
            resp = client.get(url, params={"per_page": 10})
            if resp.status_code == 200:
                releases = []
                for r in resp.json():
                    releases.append({
                        "tag": r.get("tag_name"),
                        "name": r.get("name", "")[:200],
                        "published_at": r.get("published_at"),
                        "prerelease": r.get("prerelease", False),
                        "url": r.get("html_url"),
                        "body_preview": r.get("body", "")[:500],
                    })
                return releases
    except Exception as e:
        return [{"error": str(e)[:200]}]
    return []


def fetch_recent_commits(owner: str, repo: str) -> list:
    """Fetch recent commits to detect content changes."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    try:
        with httpx.Client(timeout=15, headers=HEADERS) as client:
            resp = client.get(url, params={"per_page": 20})
            if resp.status_code == 200:
                commits = []
                for c in resp.json():
                    msg = c.get("commit", {}).get("message", "")
                    commits.append({
                        "sha": c.get("sha", "")[:8],
                        "message": msg[:300],
                        "date": c.get("commit", {}).get("author", {}).get("date"),
                        "author": c.get("commit", {}).get("author", {}).get("name"),
                        "url": c.get("html_url"),
                        "is_vulnerability_update": any(
                            kw in msg.lower()
                            for kw in ["vuln", "llm0", "risk", "threat", "attack",
                                       "injection", "poisoning", "disclosure"]
                        ),
                    })
                return commits
    except Exception as e:
        return [{"error": str(e)[:200]}]
    return []


def fetch_open_issues(owner: str, repo: str) -> dict:
    """Fetch open issues to track community discussion on vulnerabilities."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    try:
        with httpx.Client(timeout=15, headers=HEADERS) as client:
            resp = client.get(url, params={"per_page": 15, "state": "open", "sort": "updated"})
            if resp.status_code == 200:
                issues = []
                for i in resp.json():
                    if i.get("pull_request"):
                        continue  # Skip PRs
                    issues.append({
                        "number": i.get("number"),
                        "title": i.get("title", "")[:200],
                        "state": i.get("state"),
                        "created_at": i.get("created_at"),
                        "updated_at": i.get("updated_at"),
                        "comments": i.get("comments", 0),
                        "labels": [l.get("name") for l in i.get("labels", [])],
                        "url": i.get("html_url"),
                    })
                return {"issues": issues, "count": len(issues)}
    except Exception as e:
        return {"error": str(e)[:200]}
    return {"issues": [], "count": 0}


def fetch_repo_metadata(owner: str, repo: str) -> dict:
    """Fetch repo metadata for activity signals."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        with httpx.Client(timeout=15, headers=HEADERS) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "stars": data.get("stargazers_count", 0),
                    "forks": data.get("forks_count", 0),
                    "open_issues": data.get("open_issues_count", 0),
                    "last_push": data.get("pushed_at"),
                    "license": data.get("license", {}).get("spdx_id"),
                }
    except Exception:
        pass
    return {}


def run():
    """Track all OWASP AI security repos and compile intelligence."""
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting OWASP release tracker...")

    repo_data = {}
    for name, config in OWASP_REPOS.items():
        owner, repo = config["owner"], config["repo"]
        print(f"  Tracking {name} ({owner}/{repo})...")

        metadata = fetch_repo_metadata(owner, repo)
        releases = fetch_repo_releases(owner, repo)
        commits = fetch_recent_commits(owner, repo)
        issues = fetch_open_issues(owner, repo)

        vuln_commits = [c for c in commits if c.get("is_vulnerability_update")]

        repo_data[name] = {
            "description": config["description"],
            "metadata": metadata,
            "latest_release": releases[0] if releases and "error" not in releases[0] else None,
            "total_releases": len([r for r in releases if "error" not in r]),
            "recent_commits": commits[:10],
            "vulnerability_related_commits": vuln_commits,
            "open_issues": issues,
            "activity_signal": {
                "commits_last_20": len(commits),
                "vuln_commits": len(vuln_commits),
                "active": len(commits) > 0,
            },
        }
        print(f"    -> {len(commits)} commits, {len(vuln_commits)} vuln-related")

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repos": repo_data,
        "summary": {
            "repos_tracked": len(repo_data),
            "total_vuln_commits": sum(
                len(r.get("vulnerability_related_commits", [])) for r in repo_data.values()
            ),
            "most_active": max(
                repo_data.keys(),
                key=lambda k: repo_data[k].get("activity_signal", {}).get("commits_last_20", 0),
            ) if repo_data else None,
        },
    }

    out_path = OUTPUT_DIR / "owasp_release_tracker.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Written to {out_path}")
    return output


if __name__ == "__main__":
    run()
