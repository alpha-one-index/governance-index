"""
OWASP Top 10 for LLM Applications Tracker
Tracks the OWASP LLM Top 10 vulnerabilities, maps them to
mitigation controls, and monitors the OWASP GitHub repo for updates.
"""
import requests
import json
from datetime import datetime, timezone


OWASP_LLM_REPO = "https://api.github.com/repos/OWASP/www-project-top-10-for-large-language-model-applications"

# OWASP Top 10 for LLM Applications 2025
OWASP_LLM_TOP10 = [
    {"id": "LLM01", "name": "Prompt Injection", "severity": "critical", "eu_ai_act_article": "Art. 15"},
    {"id": "LLM02", "name": "Sensitive Information Disclosure", "severity": "high", "eu_ai_act_article": "Art. 10"},
    {"id": "LLM03", "name": "Supply Chain Vulnerabilities", "severity": "high", "eu_ai_act_article": "Art. 17"},
    {"id": "LLM04", "name": "Data and Model Poisoning", "severity": "critical", "eu_ai_act_article": "Art. 10"},
    {"id": "LLM05", "name": "Improper Output Handling", "severity": "high", "eu_ai_act_article": "Art. 15"},
    {"id": "LLM06", "name": "Excessive Agency", "severity": "high", "eu_ai_act_article": "Art. 14"},
    {"id": "LLM07", "name": "System Prompt Leakage", "severity": "medium", "eu_ai_act_article": "Art. 13"},
    {"id": "LLM08", "name": "Vector and Embedding Weaknesses", "severity": "medium", "eu_ai_act_article": "Art. 15"},
    {"id": "LLM09", "name": "Misinformation", "severity": "high", "eu_ai_act_article": "Art. 50"},
    {"id": "LLM10", "name": "Unbounded Consumption", "severity": "medium", "eu_ai_act_article": "Art. 15"},
]


def scrape_owasp_llm_top10():
    """Collect OWASP LLM Top 10 risk data with regulatory cross-mappings."""
    now = datetime.now(timezone.utc)
    records = []

    # Check GitHub repo for latest update
    last_updated = None
    try:
        resp = requests.get(
            f"{OWASP_LLM_REPO}/commits?per_page=1",
            timeout=30,
            headers={"User-Agent": "GovernanceIndex/1.0 (research)"}
        )
        if resp.status_code == 200:
            commits = resp.json()
            if commits:
                last_updated = commits[0]["commit"]["committer"]["date"]
    except Exception:
        pass

    for vuln in OWASP_LLM_TOP10:
        records.append({
            "timestamp": now.isoformat(),
            "source": "owasp_llm_top10",
            "framework": "OWASP Top 10 for LLM Applications 2025",
            "vulnerability_id": vuln["id"],
            "vulnerability_name": vuln["name"],
            "severity": vuln["severity"],
            "eu_ai_act_mapping": vuln["eu_ai_act_article"],
            "jurisdiction": "global",
            "category": "security",
            "repo_last_updated": last_updated,
            "framework_version": "2025-v1",
        })

    return records


if __name__ == "__main__":
    data = scrape_owasp_llm_top10()
    print(json.dumps(data, indent=2, default=str))
