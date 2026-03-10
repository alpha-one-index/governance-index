#!/usr/bin/env python3
"""Regulatory Exposure Scorer - Proprietary scoring engine for GovernanceIndex.

Calculates each organization's regulatory exposure risk based on geographic
operations, industry sector, AI use-case risk tiers, and the evolving
regulatory landscape across jurisdictions worldwide.

This is a proprietary algorithm unique to the GovernanceIndex.
"""

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
OUTPUT_DIR = Path("exports")

# Jurisdiction risk scores (higher = more regulatory burden)
JURISDICTION_RISK = {
    "eu": 95, "uk": 80, "us_federal": 60, "us_california": 75,
    "us_colorado": 65, "us_illinois": 60, "canada": 70,
    "china": 85, "japan": 55, "south_korea": 60,
    "australia": 55, "brazil": 65, "india": 50,
    "singapore": 60, "uae": 40,
}

# AI use-case risk tiers (EU AI Act aligned)
USE_CASE_RISK_TIERS = {
    "unacceptable": 100,
    "high_risk": 80,
    "limited_risk": 45,
    "minimal_risk": 15,
}

# Industry sector multipliers
SECTOR_MULTIPLIERS = {
    "healthcare": 1.4, "finance": 1.35, "government": 1.3,
    "education": 1.2, "transportation": 1.25, "energy": 1.15,
    "insurance": 1.3, "legal": 1.2, "defense": 1.4,
    "retail": 1.0, "entertainment": 0.9, "technology": 1.1,
}

# Exposure dimension weights
EXPOSURE_WEIGHTS = {
    "jurisdictional_exposure": 0.30,
    "use_case_risk": 0.25,
    "sector_risk": 0.15,
    "compliance_readiness": 0.15,
    "regulatory_velocity": 0.10,
    "enforcement_history": 0.05,
}


def load_enriched_data() -> dict:
    path = DATA_DIR / "enriched" / "enriched_frameworks.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def score_jurisdictional_exposure(org_data: dict) -> float:
    jurisdictions = org_data.get("jurisdictions", [])
    if not jurisdictions:
        return 30.0
    risk_scores = []
    for j in jurisdictions:
        j_lower = j.lower().replace(" ", "_")
        risk = JURISDICTION_RISK.get(j_lower, 50)
        risk_scores.append(risk)
    if not risk_scores:
        return 30.0
    max_risk = max(risk_scores)
    avg_risk = statistics.mean(risk_scores)
    breadth_penalty = min(len(jurisdictions) * 3, 20)
    exposure = (max_risk * 0.6 + avg_risk * 0.4) + breadth_penalty
    return min(round(exposure, 2), 100.0)


def score_use_case_risk(org_data: dict) -> float:
    use_cases = org_data.get("ai_use_cases", [])
    if not use_cases:
        return 30.0
    risk_scores = []
    for uc in use_cases:
        tier = uc.get("risk_tier", "minimal_risk") if isinstance(uc, dict) else "minimal_risk"
        risk_scores.append(USE_CASE_RISK_TIERS.get(tier, 30))
    if not risk_scores:
        return 30.0
    return round(max(risk_scores) * 0.7 + statistics.mean(risk_scores) * 0.3, 2)


def score_sector_risk(org_data: dict) -> float:
    sector = org_data.get("sector", "technology").lower()
    multiplier = SECTOR_MULTIPLIERS.get(sector, 1.0)
    base_risk = 50.0
    return min(round(base_risk * multiplier, 2), 100.0)


def score_compliance_readiness(org_data: dict) -> float:
    readiness = org_data.get("compliance_readiness", {})
    score = 20.0
    indicators = {
        "dedicated_compliance_team": 15,
        "regulatory_monitoring": 12,
        "gap_analysis_completed": 10,
        "remediation_plan": 10,
        "legal_counsel_ai": 8,
        "regulatory_sandbox_participation": 8,
        "industry_association_member": 5,
        "certification_roadmap": 7,
        "budget_allocated": 5,
    }
    for ind, points in indicators.items():
        if readiness.get(ind):
            score += points
    return min(score, 100.0)


def score_regulatory_velocity(org_data: dict) -> float:
    jurisdictions = org_data.get("jurisdictions", [])
    high_velocity = ["eu", "us_california", "china", "uk", "canada"]
    velocity_count = sum(1 for j in jurisdictions if j.lower().replace(" ", "_") in high_velocity)
    if velocity_count >= 4:
        return 90.0
    elif velocity_count >= 2:
        return 65.0
    elif velocity_count >= 1:
        return 45.0
    return 25.0


def score_enforcement_history(org_data: dict) -> float:
    enforcements = org_data.get("enforcement_actions", [])
    if not enforcements:
        return 10.0
    score = 10.0
    for action in enforcements:
        severity = action.get("severity", "low")
        sev_scores = {"critical": 30, "high": 20, "medium": 10, "low": 5}
        score += sev_scores.get(severity, 5)
    return min(score, 100.0)


def classify_exposure(score: float) -> dict:
    if score >= 80:
        return {"level": "critical", "action": "immediate_compliance_program"}
    elif score >= 60:
        return {"level": "high", "action": "accelerate_compliance"}
    elif score >= 40:
        return {"level": "moderate", "action": "structured_roadmap"}
    elif score >= 20:
        return {"level": "low", "action": "standard_monitoring"}
    return {"level": "minimal", "action": "periodic_review"}


def compute_exposure_score(org: str, org_data: dict) -> dict:
    sub_scores = {
        "jurisdictional_exposure": score_jurisdictional_exposure(org_data),
        "use_case_risk": score_use_case_risk(org_data),
        "sector_risk": score_sector_risk(org_data),
        "compliance_readiness": score_compliance_readiness(org_data),
        "regulatory_velocity": score_regulatory_velocity(org_data),
        "enforcement_history": score_enforcement_history(org_data),
    }
    composite = sum(sub_scores[k] * EXPOSURE_WEIGHTS[k] for k in EXPOSURE_WEIGHTS)
    composite = round(composite, 1)
    classification = classify_exposure(composite)
    return {
        "organization": org,
        "exposure_score": composite,
        "exposure_classification": classification,
        "sub_scores": {k: round(v, 2) for k, v in sub_scores.items()},
        "high_exposure": composite >= 60,
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def run_exposure_scoring() -> dict:
    enriched = load_enriched_data()
    orgs = enriched.get("frameworks", enriched.get("organizations", []))
    if isinstance(orgs, dict):
        orgs = list(orgs.values())
    results = []
    for o in orgs:
        name = o.get("name", o.get("organization", "unknown"))
        result = compute_exposure_score(name, o)
        results.append(result)
    results.sort(key=lambda x: x["exposure_score"], reverse=True)
    scores = [r["exposure_score"] for r in results]
    output = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "algorithm": "Regulatory Exposure Scorer v1.0",
        "weights": EXPOSURE_WEIGHTS,
        "jurisdictions_tracked": list(JURISDICTION_RISK.keys()),
        "organizations": results,
        "summary": {
            "total_organizations": len(results),
            "high_exposure_count": sum(1 for r in results if r["high_exposure"]),
            "avg_exposure": round(statistics.mean(scores), 1) if scores else 0,
            "highest_exposure": results[0]["organization"] if results else None,
            "lowest_exposure": results[-1]["organization"] if results else None,
        },
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "regulatory_exposure_report.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Exposure scored for {len(results)} organizations")
    print(f"  Written to {out_path}")
    return output


if __name__ == "__main__":
    run_exposure_scoring()
