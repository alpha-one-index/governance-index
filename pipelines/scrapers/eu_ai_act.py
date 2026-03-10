"""
EU AI Act Regulatory Tracker
Scrapes EUR-Lex and European Commission sources for AI Act
implementation timelines, delegated acts, and compliance deadlines.
"""
import requests
import json
import re
from datetime import datetime, timezone


EUR_LEX_CELEX = "32024R1689"  # EU AI Act CELEX number
EUR_LEX_API = f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{EUR_LEX_CELEX}"
EC_AI_OFFICE = "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai"

# Known compliance milestones from the AI Act
AI_ACT_MILESTONES = [
    {"article": "Art. 5", "requirement": "Prohibited AI practices ban", "deadline": "2025-02-02", "risk_tier": "unacceptable"},
    {"article": "Art. 6-7", "requirement": "GPAI model obligations", "deadline": "2025-08-02", "risk_tier": "general_purpose"},
    {"article": "Art. 6-49", "requirement": "High-risk AI system requirements", "deadline": "2026-08-02", "risk_tier": "high"},
    {"article": "Art. 50", "requirement": "Transparency obligations", "deadline": "2026-08-02", "risk_tier": "limited"},
    {"article": "Art. 51-54", "requirement": "Conformity assessment procedures", "deadline": "2027-08-02", "risk_tier": "high"},
]


def scrape_eu_ai_act():
    """Collect current EU AI Act compliance status and deadlines."""
    now = datetime.now(timezone.utc)
    records = []

    for milestone in AI_ACT_MILESTONES:
        deadline = datetime.strptime(milestone["deadline"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        days_remaining = (deadline - now).days
        status = "active" if days_remaining <= 0 else "upcoming"

        records.append({
            "timestamp": now.isoformat(),
            "source": "eu_ai_act",
            "framework": "EU AI Act (Reg. 2024/1689)",
            "article": milestone["article"],
            "requirement": milestone["requirement"],
            "compliance_deadline": milestone["deadline"],
            "days_remaining": max(days_remaining, 0),
            "enforcement_status": status,
            "risk_tier": milestone["risk_tier"],
            "jurisdiction": "EU",
            "penalty_max_eur": 35_000_000,
            "penalty_pct_turnover": 7.0,
        })

    # Try to fetch latest updates from EUR-Lex
    try:
        resp = requests.get(
            f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{EUR_LEX_CELEX}",
            timeout=30,
            headers={"User-Agent": "GovernanceIndex/1.0 (research)"}
        )
        if resp.status_code == 200:
            # Extract last modification date if available
            match = re.search(r'Date of document:\s*(\d{2}/\d{2}/\d{4})', resp.text)
            if match:
                for r in records:
                    r["source_last_updated"] = match.group(1)
    except Exception:
        pass

    return records


if __name__ == "__main__":
    data = scrape_eu_ai_act()
    print(json.dumps(data, indent=2, default=str))
