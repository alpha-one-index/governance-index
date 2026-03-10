"""
GovernanceIndex Enrichment Pipeline
Adds cross-framework mappings, risk scores, and compliance gap analysis.
The proprietary GovernanceScore is computed here (null in public exports).
"""
import json
from datetime import datetime, timezone
from pathlib import Path


EXPORT_DIR = Path("exports")

# Risk tier weights for composite scoring
RISK_WEIGHTS = {
    "critical": 1.0,
    "high": 0.75,
    "medium": 0.5,
    "low": 0.25,
    "unacceptable": 1.0,
    "general_purpose": 0.6,
    "limited": 0.4,
}


def enrich_records(records):
    """Add enrichment fields to collected governance records."""
    now = datetime.now(timezone.utc)

    for record in records:
        # Add enrichment timestamp
        record["enriched_at"] = now.isoformat()

        # Cross-framework compliance mapping
        source = record.get("source", "")

        if source == "eu_ai_act":
            risk_tier = record.get("risk_tier", "")
            record["risk_weight"] = RISK_WEIGHTS.get(risk_tier, 0.5)
            record["compliance_urgency"] = "immediate" if record.get("days_remaining", 999) <= 90 else "standard"
            record["affects_us_companies"] = True  # EU AI Act has extraterritorial scope

        elif source == "nist_ai_rmf":
            record["risk_weight"] = 0.5  # Voluntary framework
            record["compliance_urgency"] = "advisory"
            record["affects_eu_companies"] = True  # Cross-applicable best practice

        elif source == "owasp_llm_top10":
            severity = record.get("severity", "medium")
            record["risk_weight"] = RISK_WEIGHTS.get(severity, 0.5)
            record["compliance_urgency"] = "immediate" if severity == "critical" else "standard"
            record["nist_csf_mapping"] = "PR.DS"  # Data Security function

        # Proprietary GovernanceScore (null in public exports)
        record["governance_score"] = None

    return records


def run_enrichment():
    """Load collected data, enrich, and re-export."""
    json_path = EXPORT_DIR / "latest.json"

    if not json_path.exists():
        print("No collected data found. Run collect.py first.")
        return

    with open(json_path) as f:
        records = json.load(f)

    print(f"Enriching {len(records)} records...")
    enriched = enrich_records(records)

    with open(json_path, "w") as f:
        json.dump(enriched, f, indent=2, default=str)

    print(f"Enrichment complete. {len(enriched)} records updated.")
    return enriched


if __name__ == "__main__":
    run_enrichment()
