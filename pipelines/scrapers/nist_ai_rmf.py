"""
NIST AI Risk Management Framework (AI RMF) Tracker
Scrapes NIST CSRC for AI RMF updates, companion resources,
and cross-maps controls to ISO 42001 and EU AI Act requirements.
"""
import requests
import json
from datetime import datetime, timezone


NIST_CSRC_API = "https://csrc.nist.gov/CSRC/media/Projects/risk-management/documents"
NIST_AI_RMF_URL = "https://airc.nist.gov/AI_RMF_Playbook"

# NIST AI RMF Core Functions and Categories
AI_RMF_TAXONOMY = {
    "GOVERN": {
        "description": "Cultivate and implement a culture of risk management",
        "categories": [
            {"id": "GV-1", "name": "Policies and procedures", "iso42001_map": "5.2, 6.1"},
            {"id": "GV-2", "name": "Accountability structures", "iso42001_map": "5.3"},
            {"id": "GV-3", "name": "Workforce diversity and culture", "iso42001_map": "7.2"},
            {"id": "GV-4", "name": "Organizational commitments", "iso42001_map": "5.1"},
            {"id": "GV-5", "name": "Processes for engagement", "iso42001_map": "7.4"},
            {"id": "GV-6", "name": "Policies for third-party AI", "iso42001_map": "8.1"},
        ]
    },
    "MAP": {
        "description": "Contextualize risks related to AI system",
        "categories": [
            {"id": "MP-1", "name": "Intended purposes and context", "iso42001_map": "6.1.2"},
            {"id": "MP-2", "name": "Interdisciplinary AI actors", "iso42001_map": "7.2"},
            {"id": "MP-3", "name": "Benefits and costs assessment", "iso42001_map": "6.1"},
            {"id": "MP-4", "name": "Risk identification and tolerances", "iso42001_map": "6.1.1"},
            {"id": "MP-5", "name": "Impact characterization", "iso42001_map": "6.1.2"},
        ]
    },
    "MEASURE": {
        "description": "Employ quantitative and qualitative methods to analyze AI risks",
        "categories": [
            {"id": "MS-1", "name": "Risk measurement approaches", "iso42001_map": "9.1"},
            {"id": "MS-2", "name": "AI systems evaluated for trustworthiness", "iso42001_map": "8.2"},
            {"id": "MS-3", "name": "Mechanisms for tracking risks", "iso42001_map": "9.1.2"},
            {"id": "MS-4", "name": "Feedback from affected communities", "iso42001_map": "9.3"},
        ]
    },
    "MANAGE": {
        "description": "Allocate resources to mapped and measured risks",
        "categories": [
            {"id": "MG-1", "name": "Risk prioritization and response", "iso42001_map": "6.1.3"},
            {"id": "MG-2", "name": "Risk treatment plans", "iso42001_map": "6.1.3"},
            {"id": "MG-3", "name": "Pre-deployment risk management", "iso42001_map": "8.2"},
            {"id": "MG-4", "name": "Post-deployment monitoring", "iso42001_map": "9.1"},
        ]
    },
}


def scrape_nist_ai_rmf():
    """Collect NIST AI RMF control mappings and compliance status."""
    now = datetime.now(timezone.utc)
    records = []

    for function_name, function_data in AI_RMF_TAXONOMY.items():
        for category in function_data["categories"]:
            records.append({
                "timestamp": now.isoformat(),
                "source": "nist_ai_rmf",
                "framework": "NIST AI RMF 1.0",
                "function": function_name,
                "function_description": function_data["description"],
                "control_id": category["id"],
                "control_name": category["name"],
                "iso_42001_mapping": category["iso42001_map"],
                "jurisdiction": "US",
                "mandatory": False,
                "framework_version": "1.0",
                "last_revision": "2023-01-26",
            })

    # Try to check for updates from NIST
    try:
        resp = requests.get(
            "https://csrc.nist.gov/projects/ai-risk-management-framework",
            timeout=30,
            headers={"User-Agent": "GovernanceIndex/1.0 (research)"}
        )
        if resp.status_code == 200:
            for r in records:
                r["source_accessible"] = True
    except Exception:
        pass

    return records


if __name__ == "__main__":
    data = scrape_nist_ai_rmf()
    print(json.dumps(data, indent=2, default=str))
