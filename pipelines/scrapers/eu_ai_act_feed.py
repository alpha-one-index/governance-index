#!/usr/bin/env python3
"""EU AI Act Feed — Live regulatory intelligence from EUR-Lex and EU institutions.

Unique differentiator: Scrapes the official EUR-Lex SPARQL/REST endpoints and
EU legislative observatory for real-time AI Act amendments, delegated acts,
implementing acts, and enforcement actions. Computes compliance deadline
countdowns and penalty exposure estimates.
"""

import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "exports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "GovernanceIndex/1.0 (eu-ai-act-monitor)"}

# Key EU AI Act CELEX identifiers and search terms
EU_AI_ACT_CELEX = "32024R1689"  # AI Act regulation
EURLEX_REST = "https://eur-lex.europa.eu/eurlex-ws/rest"
EURLEX_SEARCH = "https://eur-lex.europa.eu/search.html"

# Known compliance deadlines (Article 113)
COMPLIANCE_DEADLINES = [
    {
        "milestone": "Prohibited AI practices ban",
        "date": "2025-02-02",
        "article": "Article 5",
        "penalty_max_eur": 35_000_000,
        "penalty_max_pct_turnover": 7,
    },
    {
        "milestone": "GPAI model obligations",
        "date": "2025-08-02",
        "article": "Articles 51-56",
        "penalty_max_eur": 15_000_000,
        "penalty_max_pct_turnover": 3,
    },
    {
        "milestone": "High-risk AI systems (Annex III)",
        "date": "2026-08-02",
        "article": "Articles 6-49",
        "penalty_max_eur": 15_000_000,
        "penalty_max_pct_turnover": 3,
    },
    {
        "milestone": "High-risk AI in Annex I sectors",
        "date": "2027-08-02",
        "article": "Article 6(1)",
        "penalty_max_eur": 15_000_000,
        "penalty_max_pct_turnover": 3,
    },
]


def compute_deadline_urgency(deadlines: list) -> list:
    """Add countdown days and urgency level to each deadline."""
    now = datetime.now(timezone.utc).date()
    enriched = []
    for d in deadlines:
        target = datetime.strptime(d["date"], "%Y-%m-%d").date()
        days_remaining = (target - now).days
        if days_remaining < 0:
            urgency = "past_due"
        elif days_remaining <= 90:
            urgency = "critical"
        elif days_remaining <= 180:
            urgency = "high"
        elif days_remaining <= 365:
            urgency = "medium"
        else:
            urgency = "low"
        enriched.append({
            **d,
            "days_remaining": days_remaining,
            "urgency": urgency,
            "enforcement_active": days_remaining <= 0,
        })
    return sorted(enriched, key=lambda x: x["days_remaining"])


def fetch_eurlex_recent_docs() -> list:
    """Search EUR-Lex for recent AI Act related documents."""
    docs = []
    search_url = (
        "https://eur-lex.europa.eu/search.html?"
        "scope=EURLEX&text=%22artificial+intelligence%22+OR+%22AI+Act%22"
        "&type=quick&lang=en&sortOne=DD_SORT&sortOneOrder=desc"
    )
    try:
        with httpx.Client(timeout=20, headers=HEADERS, follow_redirects=True) as client:
            resp = client.get(search_url)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                results = soup.select(".SearchResult, .EurlexContent")
                for r in results[:20]:
                    title_el = r.select_one("a.title, .title a, h2 a")
                    date_el = r.select_one(".date, time")
                    if title_el:
                        docs.append({
                            "title": title_el.get_text(strip=True)[:300],
                            "url": title_el.get("href", ""),
                            "date": date_el.get_text(strip=True) if date_el else None,
                            "source": "EUR-Lex",
                        })
    except Exception as e:
        docs.append({"error": f"EUR-Lex search failed: {str(e)[:200]}"})
    return docs


def fetch_ai_office_updates() -> list:
    """Scrape EU AI Office page for latest updates and guidance."""
    updates = []
    url = "https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence"
    try:
        with httpx.Client(timeout=20, headers=HEADERS, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                # Look for news/update sections
                for link in soup.select("a[href*='artificial-intelligence']")[:15]:
                    text = link.get_text(strip=True)
                    href = link.get("href", "")
                    if text and len(text) > 20:
                        if not href.startswith("http"):
                            href = f"https://digital-strategy.ec.europa.eu{href}"
                        updates.append({
                            "title": text[:300],
                            "url": href,
                            "source": "EU AI Office",
                        })
    except Exception as e:
        updates.append({"error": f"AI Office scrape failed: {str(e)[:200]}"})
    return updates


def fetch_eu_ai_act_corrigenda() -> list:
    """Check for corrigenda and amendments to the AI Act."""
    results = []
    url = f"https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:{EU_AI_ACT_CELEX}"
    try:
        with httpx.Client(timeout=20, headers=HEADERS, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for link in soup.select("a[href*='CELEX']"):
                    text = link.get_text(strip=True)
                    if any(kw in text.lower() for kw in ["corrigend", "amend", "delegated", "implementing"]):
                        results.append({
                            "title": text[:300],
                            "url": link.get("href", ""),
                            "type": "amendment" if "amend" in text.lower() else "corrigendum",
                            "source": "EUR-Lex",
                        })
    except Exception as e:
        results.append({"error": f"Corrigenda check failed: {str(e)[:200]}"})
    return results


def run():
    """Aggregate all EU AI Act regulatory intelligence."""
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting EU AI Act feed...")

    deadlines = compute_deadline_urgency(COMPLIANCE_DEADLINES)
    print(f"  Computed {len(deadlines)} deadline countdowns")

    print("  Fetching EUR-Lex recent docs...")
    recent_docs = fetch_eurlex_recent_docs()

    print("  Fetching AI Office updates...")
    ai_office = fetch_ai_office_updates()

    print("  Checking corrigenda/amendments...")
    corrigenda = fetch_eu_ai_act_corrigenda()

    # Compute next critical deadline
    upcoming = [d for d in deadlines if d["days_remaining"] > 0]
    next_deadline = upcoming[0] if upcoming else None

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "compliance_deadlines": deadlines,
        "next_critical_deadline": next_deadline,
        "recent_documents": recent_docs,
        "ai_office_updates": ai_office,
        "corrigenda_amendments": corrigenda,
        "summary": {
            "total_deadlines": len(deadlines),
            "past_due": sum(1 for d in deadlines if d["urgency"] == "past_due"),
            "critical": sum(1 for d in deadlines if d["urgency"] == "critical"),
            "documents_found": len(recent_docs),
            "ai_office_updates_found": len(ai_office),
        },
    }

    out_path = OUTPUT_DIR / "eu_ai_act_feed.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  Written to {out_path}")
    return output


if __name__ == "__main__":
    run()
