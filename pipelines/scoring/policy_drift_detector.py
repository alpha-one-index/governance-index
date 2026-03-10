#!/usr/bin/env python3
"""Policy Drift Detector - Proprietary scoring engine for GovernanceIndex.

Detects policy-to-practice drift by comparing documented governance policies
against actual implementation signals, identifying gaps where organizations
have policies on paper but fail to enforce them in practice.

This is a proprietary algorithm unique to the GovernanceIndex.
"""

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
OUTPUT_DIR = Path("exports")

# Drift dimension weights
DRIFT_WEIGHTS = {
    "policy_practice_alignment": 0.25,
    "update_currency": 0.20,
    "enforcement_evidence": 0.20,
    "regulatory_alignment": 0.15,
    "stakeholder_awareness": 0.10,
    "documentation_quality": 0.10,
}

# Key regulatory frameworks to track alignment
REGULATORY_FRAMEWORKS = [
    "eu_ai_act", "nist_ai_rmf", "iso_42001", "oecd_ai_principles",
    "unesco_ai_recommendation", "singapore_ai_governance",
    "canada_aida", "brazil_ai_framework",
]


def load_enriched_data() -> dict:
    path = DATA_DIR / "enriched" / "enriched_frameworks.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def score_policy_practice_alignment(org_data: dict) -> float:
    policies = org_data.get("policies", {})
    practices = org_data.get("practices", {})
    if not policies:
        return 0.0
    aligned = 0
    total = 0
    for policy_name, policy_exists in policies.items():
        if policy_exists:
            total += 1
            practice_key = f"{policy_name}_implemented"
            if practices.get(practice_key) or practices.get(policy_name):
                aligned += 1
    if total == 0:
        return 0.0
    return round((aligned / total) * 100, 2)


def score_update_currency(org_data: dict) -> float:
    policies = org_data.get("policies", {})
    now = datetime.now(timezone.utc)
    scores = []
    for pol_name, pol_data in policies.items():
        if isinstance(pol_data, dict):
            last_updated = pol_data.get("last_updated")
            if last_updated:
                try:
                    updated = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                    months_old = (now - updated).days / 30.44
                    if months_old <= 6:
                        scores.append(100)
                    elif months_old <= 12:
                        scores.append(80)
                    elif months_old <= 24:
                        scores.append(50)
                    else:
                        scores.append(20)
                except (ValueError, AttributeError):
                    scores.append(30)
            else:
                scores.append(30)
    if not scores:
        return 40.0
    return round(statistics.mean(scores), 2)


def score_enforcement_evidence(org_data: dict) -> float:
    score = 20.0
    enforcement = org_data.get("enforcement_evidence", {})
    evidence_types = {
        "automated_policy_checks": 15,
        "violation_records": 10,
        "audit_findings_tracked": 12,
        "remediation_evidence": 10,
        "training_completion_records": 8,
        "compliance_dashboards": 10,
        "incident_post_mortems": 8,
        "policy_exception_process": 7,
    }
    for evidence, points in evidence_types.items():
        if enforcement.get(evidence):
            score += points
    return min(score, 100.0)


def score_regulatory_alignment(org_data: dict) -> float:
    alignment = org_data.get("regulatory_alignment", {})
    if not alignment:
        return 20.0
    aligned = 0
    for framework in REGULATORY_FRAMEWORKS:
        fw_data = alignment.get(framework, {})
        if isinstance(fw_data, bool) and fw_data:
            aligned += 1
        elif isinstance(fw_data, dict) and fw_data.get("aligned"):
            aligned += 1
    coverage = aligned / len(REGULATORY_FRAMEWORKS)
    return round(coverage * 100, 2)


def score_stakeholder_awareness(org_data: dict) -> float:
    score = 30.0
    awareness = org_data.get("stakeholder_awareness", {})
    if awareness.get("training_program"):
        score += 20
    if awareness.get("awareness_campaigns"):
        score += 15
    if awareness.get("policy_accessible"):
        score += 10
    if awareness.get("feedback_mechanism"):
        score += 10
    if awareness.get("role_based_training"):
        score += 15
    return min(score, 100.0)


def score_documentation_quality(org_data: dict) -> float:
    score = 25.0
    docs = org_data.get("documentation", {})
    if docs.get("version_controlled"):
        score += 15
    if docs.get("publicly_available"):
        score += 15
    if docs.get("plain_language"):
        score += 10
    if docs.get("examples_included"):
        score += 10
    if docs.get("translated"):
        score += 10
    if docs.get("searchable"):
        score += 10
    if docs.get("linked_to_procedures"):
        score += 5
    return min(score, 100.0)


def classify_drift(score: float) -> dict:
    if score >= 85:
        return {"level": "minimal", "action": "maintain"}
    elif score >= 70:
        return {"level": "low", "action": "monitor"}
    elif score >= 50:
        return {"level": "moderate", "action": "review_and_update"}
    elif score >= 30:
        return {"level": "significant", "action": "immediate_remediation"}
    return {"level": "critical", "action": "overhaul_required"}


def compute_drift_score(org: str, org_data: dict) -> dict:
    sub_scores = {
        "policy_practice_alignment": score_policy_practice_alignment(org_data),
        "update_currency": score_update_currency(org_data),
        "enforcement_evidence": score_enforcement_evidence(org_data),
        "regulatory_alignment": score_regulatory_alignment(org_data),
        "stakeholder_awareness": score_stakeholder_awareness(org_data),
        "documentation_quality": score_documentation_quality(org_data),
    }
    composite = sum(sub_scores[k] * DRIFT_WEIGHTS[k] for k in DRIFT_WEIGHTS)
    composite = round(composite, 1)
    drift_class = classify_drift(composite)
    return {
        "organization": org,
        "drift_score": composite,
        "drift_classification": drift_class,
        "sub_scores": {k: round(v, 2) for k, v in sub_scores.items()},
        "policy_aligned": composite >= 65,
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def run_drift_detection() -> dict:
    enriched = load_enriched_data()
    orgs = enriched.get("frameworks", enriched.get("organizations", []))
    if isinstance(orgs, dict):
        orgs = list(orgs.values())
    results = []
    for o in orgs:
        name = o.get("name", o.get("organization", "unknown"))
        result = compute_drift_score(name, o)
        results.append(result)
    results.sort(key=lambda x: x["drift_score"], reverse=True)
    scores = [r["drift_score"] for r in results]
    output = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "algorithm": "Policy Drift Detector v1.0",
        "weights": DRIFT_WEIGHTS,
        "regulatory_frameworks_tracked": REGULATORY_FRAMEWORKS,
        "organizations": results,
        "summary": {
            "total_organizations": len(results),
            "policy_aligned_count": sum(1 for r in results if r["policy_aligned"]),
            "avg_drift_score": round(statistics.mean(scores), 1) if scores else 0,
            "best_aligned": results[0]["organization"] if results else None,
            "worst_drift": results[-1]["organization"] if results else None,
        },
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "policy_drift_report.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Policy drift analyzed for {len(results)} organizations")
    print(f"  Written to {out_path}")
    return output


if __name__ == "__main__":
    run_drift_detection()
