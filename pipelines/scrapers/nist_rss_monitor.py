#!/usr/bin/env python3
"""NIST RSS Monitor — Live feed of NIST AI RMF updates and CSRC publications.

Unique differentiator: Monitors NIST CSRC RSS feeds, AI RMF Playbook changes,
and new SP 800-series publications relevant to AI governance. Cross-maps
NIST controls to ISO 42001 clauses for gap analysis.
"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "exports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "GovernanceIndex/1.0 (nist-monitor)"}

# NIST feeds to monitor
NIST_FEEDS = {
    "csrc_publications": {
        "url": "https://csrc.nist.gov/CSRC/media/feeds/publication/rss",
        "type": "rss",
        "filter_keywords": ["artificial intelligence", "AI", "machine learning",
                            "AI RMF", "600-1", "trustworthy"],
    },
    "csrc_news": {
        "url": "https://csrc.nist.gov/CSRC/media/feeds/news/rss",
        "type": "rss",
        "filter_keywords": ["artificial intelligence", "AI", "machine learning",
                            "AI RMF", "trustworthy"],
    },
    "nvd_cve": {
        "url": "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=artificial+intelligence&resultsPerPage=20",
        "type": "nvd_api",
    },
}

# NIST AI RMF to ISO 42001 cross-mapping
NIST_ISO_CROSSMAP = {
    "GOVERN": {
        "nist_function": "Govern",
        "iso_42001_clauses": ["5.1", "5.2", "5.3", "6.1", "7.1"],
        "description": "Leadership, policy, risk management strategy",
    },
    "MAP": {
        "nist_function": "Map",
        "iso_42001_clauses": ["6.1.2", "8.2", "8.4"],
        "description": "Context mapping, AI system categorization",
    },
    "MEASURE": {
        "nist_function": "Measure",
        "iso_42001_clauses": ["9.1", "9.2", "9.3"],
        "description": "Performance monitoring, metrics, evaluation",
    },
    "MANAGE": {
        "nist_function": "Manage",
        "iso_42001_clauses": ["8.1", "10.1", "10.2"],
        "description": "Operational controls, incident response, improvement",
    },
}


def parse_rss_feed(xml_text: str, keywords: list) -> list:
    """Parse RSS XML and filter items by AI-related keywords."""
    items = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.iter("item"):
            title = item.findtext("title", "").strip()
            desc = item.findtext("description", "").strip()
            link = item.findtext("link", "").strip()
            pub_date = item.findtext("pubDate", "").strip()
            combined = f"{title} {desc}".lower()
            relevance = sum(1 for kw in keywords if kw.lower() in combined)
            if relevance > 0:
                items.append({
                    "title": title[:300],
                    "description": desc[:500],
                    "url": link,
                    "published": pub_date,
                    "relevance_score": relevance,
                    "matched_keywords": [kw for kw in keywords if kw.lower() in combined],
                })
    except ET.ParseError:
        items.append({"error": "Failed to parse RSS XML"})
    return sorted(items, key=lambda x: x.get("relevance_score", 0), reverse=True)


def parse_nvd_response(data: dict) -> list:
    """Parse NVD CVE API response for AI-related vulnerabilities."""
    cves = []
    for vuln in data.get("vulnerabilities", []):
        cve = vuln.get("cve", {})
        metrics = cve.get("metrics", {})
        cvss_v31 = metrics.get("cvssMetricV31", [{}])
        base_score = cvss_v31[0].get("cvssData", {}).get("baseScore", 0) if cvss_v31 else 0

        descriptions = cve.get("descriptions", [])
        en_desc = next((d["value"] for d in descriptions if d.get("lang") == "en"), "")

        cves.append({
            "cve_id": cve.get("id"),
            "description": en_desc[:500],
            "published": cve.get("published"),
            "modified": cve.get("lastModified"),
            "cvss_score": base_score,
            "severity": "critical" if base_score >= 9 else "high" if base_score >= 7 else "medium" if base_score >= 4 else "low",
        })
    return sorted(cves, key=lambda x: x.get("cvss_score", 0), reverse=True)


def fetch_ai_rmf_playbook() -> dict:
    """Check NIST AI RMF Playbook for latest suggested actions."""
    url = "https://airc.nist.gov/AI_RMF_Playbook"
    try:
        with httpx.Client(timeout=20, headers=HEADERS, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                actions = []
                for el in soup.select(".card, .action-item, [class*='playbook']")[:20]:
                    text = el.get_text(strip=True)[:300]
                    if text:
                        actions.append(text)
                return {
                    "reachable": True,
                    "suggested_actions_sample": actions[:10],
                    "total_found": len(actions),
                }
    except Exception as e:
        return {"reachable": False, "error": str(e)[:200]}
    return {"reachable": True, "suggested_actions_sample": []}


def run():
    """Fetch all NIST feeds and compile AI governance intelligence."""
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting NIST RSS monitor...")

    feed_results = {}
    for name, config in NIST_FEEDS.items():
        print(f"  Fetching {name}...")
        try:
            with httpx.Client(timeout=20, headers=HEADERS, follow_redirects=True) as client:
                resp = client.get(config["url"])
                if config["type"] == "rss":
                    items = parse_rss_feed(resp.text, config.get("filter_keywords", []))
                    feed_results[name] = {"items": items, "count": len(items)}
                elif config["type"] == "nvd_api":
                    data = resp.json()
                    cves = parse_nvd_response(data)
                    feed_results[name] = {"cves": cves, "count": len(cves)}
                print(f"    -> {feed_results[name].get('count', 0)} items")
        except Exception as e:
            feed_results[name] = {"error": str(e)[:200]}
            print(f"    -> Error: {str(e)[:100]}")

    print("  Checking AI RMF Playbook...")
    playbook = fetch_ai_rmf_playbook()

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "feeds": feed_results,
        "ai_rmf_playbook": playbook,
        "nist_iso_crossmap": NIST_ISO_CROSSMAP,
        "summary": {
            "total_publications": sum(
                r.get("count", 0) for r in feed_results.values()
            ),
            "feeds_checked": len(NIST_FEEDS),
            "crossmap_functions": len(NIST_ISO_CROSSMAP),
        },
    }

    out_path = OUTPUT_DIR / "nist_rss_monitor.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Written to {out_path}")
    return output


if __name__ == "__main__":
    run()
