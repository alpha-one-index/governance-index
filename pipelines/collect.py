"""
GovernanceIndex Collection Pipeline
Aggregates data from all governance scrapers including live regulatory
feeds, NIST monitors, and OWASP trackers into unified exports.
"""
import json
import csv
import os
from datetime import datetime, timezone
from pathlib import Path

from pipelines.scrapers.eu_ai_act import scrape_eu_ai_act
from pipelines.scrapers.nist_ai_rmf import scrape_nist_ai_rmf
from pipelines.scrapers.owasp_llm_top10 import scrape_owasp_llm_top10
from pipelines.scrapers.eu_ai_act_feed import run as run_eu_feed
from pipelines.scrapers.nist_rss_monitor import run as run_nist_monitor
from pipelines.scrapers.owasp_release_tracker import run as run_owasp_tracker

EXPORT_DIR = Path("exports")


def collect_all():
    """Run all governance scrapers and merge results."""
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting GovernanceIndex collection...")

    all_records = []

    # --- Core framework scrapers ---
    # EU AI Act
    try:
        eu_data = scrape_eu_ai_act()
        all_records.extend(eu_data)
        print(f"  EU AI Act: {len(eu_data)} records")
    except Exception as e:
        print(f"  EU AI Act FAILED: {e}")

    # NIST AI RMF
    try:
        nist_data = scrape_nist_ai_rmf()
        all_records.extend(nist_data)
        print(f"  NIST AI RMF: {len(nist_data)} records")
    except Exception as e:
        print(f"  NIST AI RMF FAILED: {e}")

    # OWASP LLM Top 10
    try:
        owasp_data = scrape_owasp_llm_top10()
        all_records.extend(owasp_data)
        print(f"  OWASP LLM Top 10: {len(owasp_data)} records")
    except Exception as e:
        print(f"  OWASP LLM Top 10 FAILED: {e}")

    # Export core records
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    with open(EXPORT_DIR / "governance_index.json", "w") as f:
        json.dump({
            "generated": ts,
            "framework": "GovernanceIndex",
            "count": len(all_records),
            "records": all_records,
        }, f, indent=2)

    if all_records:
        all_keys = []
        seen = set()
        for r in all_records:
            for k in r.keys():
                if k not in seen:
                    all_keys.append(k)
                    seen.add(k)
        with open(EXPORT_DIR / "governance_index.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore", restval="")
            writer.writeheader()
            writer.writerows(all_records)

    print(f"  [export] {len(all_records)} core records exported ({ts})")

    # --- Live regulatory intelligence feeds (unique differentiators) ---
    print("\n--- Running live EU AI Act feed ---")
    try:
        eu_feed = run_eu_feed()
        print(f"  [eu_feed] {eu_feed['summary']['total_deadlines']} deadlines tracked")
    except Exception as e:
        print(f"  [eu_feed] FAILED: {e}")

    print("\n--- Running NIST RSS monitor ---")
    try:
        nist_feed = run_nist_monitor()
        print(f"  [nist_monitor] {nist_feed['summary']['total_publications']} publications found")
    except Exception as e:
        print(f"  [nist_monitor] FAILED: {e}")

    print("\n--- Running OWASP release tracker ---")
    try:
        owasp_feed = run_owasp_tracker()
        print(f"  [owasp_tracker] {owasp_feed['summary']['repos_tracked']} repos tracked")
    except Exception as e:
        print(f"  [owasp_tracker] FAILED: {e}")


if __name__ == "__main__":
    collect_all()
