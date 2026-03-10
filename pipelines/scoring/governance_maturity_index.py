#!/usr/bin/env python3
"""Governance Maturity Index - Proprietary scoring engine for GovernanceIndex.

Assesses AI governance maturity across organizations by evaluating policy
completeness, enforcement mechanisms, audit practices, stakeholder
accountability, and continuous improvement processes.

This is a proprietary algorithm unique to the GovernanceIndex.
"""

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
OUTPUT_DIR = Path("exports")

# Maturity dimension weights
MATURITY_WEIGHTS = {
    "policy_completeness": 0.20,
    "enforcement_strength": 0.20,
    "audit_practices": 0.15,
    "stakeholder_accountability": 0.15,
    "risk_management": 0.10,
    "transparency_reporting": 0.10,
    "continuous_improvement": 0.10,
}

# Maturity levels (CMMI-inspired)
MATURITY_LEVELS = {
    1: {"name": "Initial", "min": 0, "description": "Ad-hoc, reactive governance"},
    2: {"name": "Developing", "min": 25, "description": "Basic policies exist but inconsistent"},
    3: {"name": "Defined", "min": 50, "description": "Standardized processes in place"},
    4: {"name": "Managed", "min": 70, "description": "Quantitatively managed and measured"},
    5: {"name": "Optimizing", "min": 85, "description": "Continuous improvement driven"},
}

# Required governance policies
REQUIRED_POLICIES = [
    "ai_ethics_policy", "data_governance_policy", "model_risk_management",
    "bias_mitigation_policy", "transparency_policy", "incident_response",
    "human_oversight_policy", "privacy_impact_assessment", "third_party_ai_policy",
    "ai_acceptable_use_policy",
]


def load_enriched_data() -> dict:
    path = DATA_DIR / "enriched" / "enriched_frameworks.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def score_policy_completeness(org_data: dict) -> float:
    policies = org_data.get("policies", {})
    found = 0
    for pol in REQUIRED_POLICIES:
        if policies.get(pol):
            found += 1
    base = (found / len(REQUIRED_POLICIES)) * 80
    if policies.get("policy_review_schedule"):
        base += 10
    if policies.get("policy_version_control"):
        base += 10
    return min(round(base, 2), 100.0)


def score_enforcement_strength(org_data: dict) -> float:
    score = 0.0
    enforcement = org_data.get("enforcement", {})
    mechanisms = {
        "automated_checks": 20,
        "pre_deployment_review": 15,
        "model_registry_required": 15,
        "approval_workflow": 10,
        "compliance_gates": 10,
        "violation_tracking": 10,
        "escalation_process": 10,
        "sanctions_defined": 5,
        "training_mandatory": 5,
    }
    for mech, points in mechanisms.items():
        if enforcement.get(mech):
            score += points
    return min(score, 100.0)


def score_audit_practices(org_data: dict) -> float:
    score = 30.0
    audit = org_data.get("audit", {})
    if audit.get("regular_audits"):
        score += 20
    if audit.get("external_audits"):
        score += 15
    if audit.get("audit_trail_logging"):
        score += 15
    if audit.get("model_lineage_tracking"):
        score += 10
    if audit.get("data_lineage_tracking"):
        score += 10
    freq = audit.get("audit_frequency_months", 0)
    if 0 < freq <= 6:
        score += 10
    elif 0 < freq <= 12:
        score += 5
    return min(max(score, 0.0), 100.0)


def score_stakeholder_accountability(org_data: dict) -> float:
    score = 20.0
    accountability = org_data.get("accountability", {})
    roles = {
        "chief_ai_officer": 15,
        "ai_ethics_board": 15,
        "responsible_ai_team": 12,
        "data_protection_officer": 10,
        "model_owners_defined": 10,
        "raci_matrix": 8,
        "board_oversight": 10,
    }
    for role, points in roles.items():
        if accountability.get(role):
            score += points
    return min(score, 100.0)


def score_risk_management(org_data: dict) -> float:
    score = 25.0
    risk = org_data.get("risk_management", {})
    if risk.get("risk_framework"):
        score += 20
    if risk.get("risk_register"):
        score += 15
    if risk.get("impact_assessments"):
        score += 15
    if risk.get("risk_appetite_defined"):
        score += 10
    if risk.get("continuous_monitoring"):
        score += 15
    return min(score, 100.0)


def score_transparency_reporting(org_data: dict) -> float:
    score = 20.0
    transparency = org_data.get("transparency", {})
    if transparency.get("public_ai_registry"):
        score += 20
    if transparency.get("model_cards"):
        score += 15
    if transparency.get("annual_ai_report"):
        score += 15
    if transparency.get("explainability_tools"):
        score += 15
    if transparency.get("stakeholder_communication"):
        score += 10
    if transparency.get("incident_disclosure"):
        score += 5
    return min(score, 100.0)


def score_continuous_improvement(org_data: dict) -> float:
    score = 30.0
    improvement = org_data.get("improvement", {})
    if improvement.get("feedback_loops"):
        score += 15
    if improvement.get("benchmarking"):
        score += 15
    if improvement.get("lessons_learned"):
        score += 10
    if improvement.get("innovation_tracking"):
        score += 10
    if improvement.get("regulatory_horizon_scanning"):
        score += 10
    if improvement.get("maturity_self_assessment"):
        score += 10
    return min(score, 100.0)


def determine_maturity_level(score: float) -> dict:
    level = 1
    for lvl, config in sorted(MATURITY_LEVELS.items(), reverse=True):
        if score >= config["min"]:
            level = lvl
            break
    config = MATURITY_LEVELS[level]
    return {
        "level": level,
        "name": config["name"],
        "description": config["description"],
    }


def compute_maturity_score(org: str, org_data: dict) -> dict:
    sub_scores = {
        "policy_completeness": score_policy_completeness(org_data),
        "enforcement_strength": score_enforcement_strength(org_data),
        "audit_practices": score_audit_practices(org_data),
        "stakeholder_accountability": score_stakeholder_accountability(org_data),
        "risk_management": score_risk_management(org_data),
        "transparency_reporting": score_transparency_reporting(org_data),
        "continuous_improvement": score_continuous_improvement(org_data),
    }
    composite = sum(sub_scores[k] * MATURITY_WEIGHTS[k] for k in MATURITY_WEIGHTS)
    composite = round(composite, 1)
    maturity = determine_maturity_level(composite)
    return {
        "organization": org,
        "gmi_score": composite,
        "maturity_level": maturity,
        "sub_scores": {k: round(v, 2) for k, v in sub_scores.items()},
        "governance_ready": composite >= 60,
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def run_maturity_assessment() -> dict:
    enriched = load_enriched_data()
    orgs = enriched.get("frameworks", enriched.get("organizations", []))
    if isinstance(orgs, dict):
        orgs = list(orgs.values())
    results = []
    for o in orgs:
        name = o.get("name", o.get("organization", "unknown"))
        result = compute_maturity_score(name, o)
        results.append(result)
    results.sort(key=lambda x: x["gmi_score"], reverse=True)
    scores = [r["gmi_score"] for r in results]
    output = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "algorithm": "Governance Maturity Index v1.0",
        "weights": MATURITY_WEIGHTS,
        "maturity_levels": {str(k): v for k, v in MATURITY_LEVELS.items()},
        "organizations": results,
        "summary": {
            "total_organizations": len(results),
            "governance_ready": sum(1 for r in results if r["governance_ready"]),
            "avg_gmi": round(statistics.mean(scores), 1) if scores else 0,
            "highest_maturity": results[0]["organization"] if results else None,
            "lowest_maturity": results[-1]["organization"] if results else None,
        },
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "governance_maturity_report.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Maturity assessed for {len(results)} organizations")
    print(f"  Written to {out_path}")
    return output


if __name__ == "__main__":
    run_maturity_assessment()
