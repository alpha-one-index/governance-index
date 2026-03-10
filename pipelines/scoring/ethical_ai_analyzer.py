#!/usr/bin/env python3
"""Ethical AI Analyzer - Proprietary scoring engine for GovernanceIndex.

Evaluates organizations' ethical AI posture across fairness, accountability,
transparency, safety, privacy, and human oversight dimensions using a
multi-layered scoring framework with evidence-based assessment.

This is a proprietary algorithm unique to the GovernanceIndex.
"""

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
OUTPUT_DIR = Path("exports")

# Ethical AI dimension weights
ETHICS_WEIGHTS = {
    "fairness_bias": 0.20,
    "accountability": 0.18,
    "transparency": 0.18,
    "safety_robustness": 0.15,
    "privacy_protection": 0.15,
    "human_oversight": 0.14,
}

# Ethical AI principles alignment
PRINCIPLES = [
    "beneficence", "non_maleficence", "autonomy",
    "justice", "explicability", "sustainability",
]


def load_enriched_data() -> dict:
    path = DATA_DIR / "enriched" / "enriched_frameworks.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def score_fairness_bias(org_data: dict) -> float:
    score = 15.0
    fairness = org_data.get("fairness", {})
    indicators = {
        "bias_testing_framework": 15,
        "regular_bias_audits": 12,
        "diverse_training_data": 10,
        "fairness_metrics_defined": 10,
        "bias_mitigation_tools": 10,
        "demographic_parity_checks": 8,
        "equalized_odds_testing": 8,
        "third_party_bias_audit": 7,
        "bias_incident_response": 5,
    }
    for ind, points in indicators.items():
        if fairness.get(ind):
            score += points
    return min(score, 100.0)


def score_accountability(org_data: dict) -> float:
    score = 20.0
    accountability = org_data.get("accountability", {})
    indicators = {
        "clear_ownership_model": 15,
        "decision_audit_trail": 12,
        "impact_assessment_process": 10,
        "redress_mechanism": 10,
        "liability_framework": 8,
        "whistleblower_protection": 8,
        "public_accountability_report": 7,
        "third_party_oversight": 5,
        "stakeholder_engagement": 5,
    }
    for ind, points in indicators.items():
        if accountability.get(ind):
            score += points
    return min(score, 100.0)


def score_transparency(org_data: dict) -> float:
    score = 15.0
    transparency = org_data.get("transparency", {})
    indicators = {
        "model_cards_published": 15,
        "data_sheets_available": 12,
        "algorithmic_impact_public": 10,
        "explainability_tools": 10,
        "decision_rationale_logging": 10,
        "open_source_components": 8,
        "api_documentation": 5,
        "public_ai_inventory": 8,
        "user_notification_of_ai": 7,
    }
    for ind, points in indicators.items():
        if transparency.get(ind):
            score += points
    return min(score, 100.0)


def score_safety_robustness(org_data: dict) -> float:
    score = 20.0
    safety = org_data.get("safety", {})
    indicators = {
        "adversarial_testing": 15,
        "red_teaming": 12,
        "fallback_mechanisms": 10,
        "monitoring_in_production": 10,
        "incident_response_plan": 8,
        "graceful_degradation": 8,
        "security_testing": 7,
        "performance_benchmarks": 5,
        "stress_testing": 5,
    }
    for ind, points in indicators.items():
        if safety.get(ind):
            score += points
    return min(score, 100.0)


def score_privacy_protection(org_data: dict) -> float:
    score = 20.0
    privacy = org_data.get("privacy", {})
    indicators = {
        "privacy_by_design": 15,
        "data_minimization": 12,
        "consent_management": 10,
        "anonymization_techniques": 10,
        "privacy_impact_assessment": 8,
        "data_retention_policy": 8,
        "right_to_deletion": 7,
        "differential_privacy": 5,
        "federated_learning": 5,
    }
    for ind, points in indicators.items():
        if privacy.get(ind):
            score += points
    return min(score, 100.0)


def score_human_oversight(org_data: dict) -> float:
    score = 20.0
    oversight = org_data.get("human_oversight", {})
    indicators = {
        "human_in_the_loop": 15,
        "human_on_the_loop": 10,
        "override_capability": 12,
        "escalation_to_human": 10,
        "decision_review_process": 8,
        "operator_training": 8,
        "meaningful_control": 7,
        "autonomy_levels_defined": 5,
        "kill_switch": 5,
    }
    for ind, points in indicators.items():
        if oversight.get(ind):
            score += points
    return min(score, 100.0)


def classify_ethics(score: float) -> dict:
    if score >= 85:
        return {"level": "exemplary", "badge": "ethical_leader"}
    elif score >= 70:
        return {"level": "strong", "badge": "ethical_practitioner"}
    elif score >= 50:
        return {"level": "developing", "badge": "ethical_aware"}
    elif score >= 30:
        return {"level": "basic", "badge": "needs_improvement"}
    return {"level": "insufficient", "badge": "at_risk"}


def compute_ethics_score(org: str, org_data: dict) -> dict:
    sub_scores = {
        "fairness_bias": score_fairness_bias(org_data),
        "accountability": score_accountability(org_data),
        "transparency": score_transparency(org_data),
        "safety_robustness": score_safety_robustness(org_data),
        "privacy_protection": score_privacy_protection(org_data),
        "human_oversight": score_human_oversight(org_data),
    }
    composite = sum(sub_scores[k] * ETHICS_WEIGHTS[k] for k in ETHICS_WEIGHTS)
    composite = round(composite, 1)
    classification = classify_ethics(composite)
    principles_aligned = []
    for p in PRINCIPLES:
        if org_data.get("principles", {}).get(p):
            principles_aligned.append(p)
    return {
        "organization": org,
        "ethics_score": composite,
        "ethics_classification": classification,
        "sub_scores": {k: round(v, 2) for k, v in sub_scores.items()},
        "principles_aligned": principles_aligned,
        "ethically_ready": composite >= 60,
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def run_ethics_analysis() -> dict:
    enriched = load_enriched_data()
    orgs = enriched.get("frameworks", enriched.get("organizations", []))
    if isinstance(orgs, dict):
        orgs = list(orgs.values())
    results = []
    for o in orgs:
        name = o.get("name", o.get("organization", "unknown"))
        result = compute_ethics_score(name, o)
        results.append(result)
    results.sort(key=lambda x: x["ethics_score"], reverse=True)
    scores = [r["ethics_score"] for r in results]
    output = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "algorithm": "Ethical AI Analyzer v1.0",
        "weights": ETHICS_WEIGHTS,
        "principles_tracked": PRINCIPLES,
        "organizations": results,
        "summary": {
            "total_organizations": len(results),
            "ethically_ready_count": sum(1 for r in results if r["ethically_ready"]),
            "avg_ethics_score": round(statistics.mean(scores), 1) if scores else 0,
            "ethics_leader": results[0]["organization"] if results else None,
            "most_at_risk": results[-1]["organization"] if results else None,
        },
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "ethical_ai_report.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Ethics analyzed for {len(results)} organizations")
    print(f"  Written to {out_path}")
    return output


if __name__ == "__main__":
    run_ethics_analysis()
