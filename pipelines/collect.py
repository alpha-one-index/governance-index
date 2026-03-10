"""
GovernanceIndex Collection Pipeline
Aggregates data from all governance scrapers into unified exports.
"""
import json
import csv
import os
from datetime import datetime, timezone
from pathlib import Path

from pipelines.scrapers.eu_ai_act import scrape_eu_ai_act
from pipelines.scrapers.nist_ai_rmf import scrape_nist_ai_rmf
from pipelines.scrapers.owasp_llm_top10 import scrape_owasp_llm_top10


EXPORT_DIR = Path("exports")


def collect_all():
    """Run all governance scrapers and merge results."""
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting GovernanceIndex collection...")

    all_records = []

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

    print(f"  Total: {len(all_records)} records")

    # Export
    EXPORT_DIR.mkdir(exist_ok=True)

    # JSON export
    json_path = EXPORT_DIR / "latest.json"
    with open(json_path, "w") as f:
        json.dump(all_records, f, indent=2, default=str)
    print(f"  Exported: {json_path}")

    # CSV export
    if all_records:
        csv_path = EXPORT_DIR / "latest.csv"
        all_keys = set()
        for r in all_records:
            all_keys.update(r.keys())
        fieldnames = sorted(all_keys)

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in all_records:
                writer.writerow(r)
        print(f"  Exported: {csv_path}")

    print(f"[{datetime.now(timezone.utc).isoformat()}] Collection complete.")
    return all_records


if __name__ == "__main__":
    collect_all()
