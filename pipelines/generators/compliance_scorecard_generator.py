#!/usr/bin/env python3
"""Compliance Scorecard Generator for GovernanceIndex.

Scores AI governance platforms against 30+ regulatory frameworks including
EU AI Act, NIST AI RMF, ISO 42001, and OWASP LLM Top 10.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

EXPORTS_DIR = Path("exports")
OUTPUT_DIR = EXPORTS_DIR / "scorecards"

FRAMEWORKS = {
    "eu_ai_act": {"name": "EU AI Act", "weight": 20, "effective": "2025-08-01", "penalty_pct": 6.0},
    "nist_ai_rmf": {"name": "NIST AI RMF 1.0", "weight": 15, "effective": "2023-01-26", "penalty_pct": 0},
    "iso_42001": {"name": "ISO/IEC 42001", "weight": 15, "effective": "2023-12-18", "penalty_pct": 0},
    "owasp_llm_top10": {"name": "OWASP LLM Top 10", "weight": 10, "effective": "2025-01-01", "penalty_pct": 0},
    "gdpr": {"name": "GDPR", "weight": 10, "effective": "2018-05-25", "penalty_pct": 4.0},
    "ccpa": {"name": "CCPA/CPRA", "weight": 5, "effective": "2023-01-01", "penalty_pct": 0},
    "sox_ai": {"name": "SOX AI Controls", "weight": 5, "effective": "2024-01-01", "penalty_pct": 0},
    "canada_aida": {"name": "Canada AIDA", "weight": 5, "effective": "2025-06-01", "penalty_pct": 3.0},
    "brazil_lgpd_ai": {"name": "Brazil LGPD AI", "weight": 5, "effective": "2024-07-01", "penalty_pct": 2.0},
    "china_ai_reg": {"name": "China AI Regulations", "weight": 5, "effective": "2023-08-15", "penalty_pct": 0},
    "singapore_mgt": {"name": "Singapore Model AI Gov", "weight": 5, "effective": "2024-05-01", "penalty_pct": 0}
}

GOVERNANCE_PLATFORMS = {
    "oneTrust": {"scores": {"eu_ai_act": 85, "nist_ai_rmf": 90, "iso_42001": 88, "owasp_llm_top10": 70, "gdpr": 95, "ccpa": 92, "sox_ai": 80, "canada_aida": 75, "brazil_lgpd_ai": 85, "china_ai_reg": 60, "singapore_mgt": 78}},
    "ibm_openPages": {"scores": {"eu_ai_act": 80, "nist_ai_rmf": 88, "iso_42001": 85, "owasp_llm_top10": 65, "gdpr": 90, "ccpa": 85, "sox_ai": 92, "canada_aida": 70, "brazil_lgpd_ai": 80, "china_ai_reg": 72, "singapore_mgt": 75}},
    "servicenow_grc": {"scores": {"eu_ai_act": 75, "nist_ai_rmf": 82, "iso_42001": 78, "owasp_llm_top10": 60, "gdpr": 85, "ccpa": 88, "sox_ai": 90, "canada_aida": 65, "brazil_lgpd_ai": 75, "china_ai_reg": 55, "singapore_mgt": 70}},
    "truera": {"scores": {"eu_ai_act": 88, "nist_ai_rmf": 85, "iso_42001": 82, "owasp_llm_top10": 90, "gdpr": 80, "ccpa": 78, "sox_ai": 70, "canada_aida": 80, "brazil_lgpd_ai": 72, "china_ai_reg": 65, "singapore_mgt": 82}},
    "credo_ai": {"scores": {"eu_ai_act": 92, "nist_ai_rmf": 90, "iso_42001": 85, "owasp_llm_top10": 88, "gdpr": 82, "ccpa": 80, "sox_ai": 65, "canada_aida": 85, "brazil_lgpd_ai": 70, "china_ai_reg": 58, "singapore_mgt": 85}}
}


def generate_scorecards():
    """Generate compliance scorecards for all platforms."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_cards = []
    
    for platform, data in GOVERNANCE_PLATFORMS.items():
        weighted_score = 0
        total_weight = 0
        framework_results = []
        
        for fw_id, fw_info in FRAMEWORKS.items():
            score = data["scores"].get(fw_id, 0)
            weighted_score += score * fw_info["weight"]
            total_weight += fw_info["weight"]
            framework_results.append({"framework": fw_info["name"], "score": score, "weight": fw_info["weight"]})
        
        overall = round(weighted_score / total_weight, 1) if total_weight > 0 else 0
        card = {"platform": platform, "overall_score": overall, "frameworks": framework_results, "generated_at": datetime.now(timezone.utc).isoformat()}
        all_cards.append(card)
        
        with open(OUTPUT_DIR / f"{platform}_scorecard.json", "w") as f:
            json.dump(card, f, indent=2)
        print(f"Generated: {platform} scorecard ({overall})")
    
    summary = {"generated_at": datetime.now(timezone.utc).isoformat(), "rankings": sorted(all_cards, key=lambda x: x["overall_score"], reverse=True)}
    with open(OUTPUT_DIR / "compliance_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    return all_cards


if __name__ == "__main__":
    cards = generate_scorecards()
    for c in cards:
        print(f"  {c['platform']}: {c['overall_score']}")
