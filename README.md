# GovernanceIndex — Live AI Governance TRiSM & Compliance Risk Scoring

[![Daily Update](https://img.shields.io/badge/updates-daily-brightgreen)]()
[![Frameworks](https://img.shields.io/badge/frameworks-30%2B-blue)]()
[![License](https://img.shields.io/badge/license-Apache%202.0-orange)]()

> The definitive cross-framework AI compliance tracker — regulatory risk scores, audit readiness, and framework mapping across EU AI Act, NIST AI RMF, ISO 42001, and OWASP LLM Top 10, updated daily.

## What Is GovernanceIndex?

GovernanceIndex is an **open-core dataset and API** that answers the question every CISO and compliance team needs answered:

> *"How exposed are we to AI regulatory risk — and what controls do we need across every jurisdiction we operate in?"*

Regulatory landscapes shift constantly. GovernanceIndex tracks them in real-time:

- 🏦 EU AI Act compliance deadlines, enforcement status, and penalty exposure
- 🛡️ NIST AI RMF control mappings with ISO 42001 cross-references
- 🔴 OWASP LLM Top 10 vulnerability tracking with severity scoring
- 📊 Cross-framework gap analysis (EU ↔ US ↔ ISO ↔ OWASP)
- ⚠️ Compliance urgency scoring based on upcoming deadlines

## Data Sources (All Public)

| Source | Data | Frequency |
|--------|------|-----------|
| EUR-Lex / EU AI Act | Compliance deadlines and enforcement status | Daily |
| NIST CSRC | AI RMF controls and companion resources | Daily |
| OWASP GitHub | LLM Top 10 vulnerabilities and updates | Daily |
| ISO 42001 Registry | AI management system standard mappings | Daily |
| National AI Policy Trackers | Global regulatory landscape changes | Daily |
| EUR-Lex Live Feed | Real-time AI Act amendments and corrigenda | Daily |
| EU AI Office | Guidance documents and enforcement updates | Daily |
| NIST CSRC RSS | AI RMF publications and news feed | Daily |
| NVD CVE API | AI-related vulnerability disclosures | Daily |
| OWASP GitHub Tracker | LLM Top 10 commits, releases, and issues | Daily |
| NIST-ISO Crossmap | AI RMF to ISO 42001 control mappings | Daily |

## Schema

All exports follow the [GovernanceIndex Schema v1](schemas/schema_v1.json):

```json
{
  "timestamp": "2026-03-09T06:00:00Z",
  "source": "eu_ai_act",
  "framework": "EU AI Act (Reg. 2024/1689)",
  "article": "Art. 6-49",
  "requirement": "High-risk AI system requirements",
  "compliance_deadline": "2026-08-02",
  "days_remaining": 146,
  "enforcement_status": "upcoming",
  "risk_tier": "high",
  "jurisdiction": "EU",
  "penalty_max_eur": 35000000,
  "penalty_pct_turnover": 7.0,
  "governance_score": null
}
```

> **Note:** `governance_score` (the proprietary composite compliance risk score) is available in the [paid API/dataset](https://aws.amazon.com/marketplace).

## Exports

| Format | Location | Access |
|--------|----------|--------|
| CSV | `exports/latest.csv` | Free (this repo) |
| JSON | `exports/latest.json` | Free (this repo) |
| JSON API | `api.governanceindex.com/v1/` | Free tier (100 req/day) |
| Full History + Score | AWS Data Exchange | Paid subscription |

## Methodology

Full methodology is documented in [docs/methodology.md](docs/methodology.md). All source code for data collection is open. The proprietary risk normalization engine and GovernanceScore algorithm are closed-source but the inputs and methodology principles are fully disclosed.

## Quick Start

```bash
# Clone and install
git clone https://github.com/alpha-one-index/governance-index.git
cd governance-index
pip install -r requirements.txt

# Run a single collection cycle
python -m pipelines.collect

# Run with enrichment
python -m pipelines.enrich
```

## License

Data collection pipelines: **Apache 2.0** (use freely)

GovernanceIndex dataset exports: **CC BY 4.0** (cite us)

GovernanceScore engine: **Proprietary** (available via paid API/AWS DX)

---

*Part of the [Alpha One Index](https://alphaoneindex.com) ecosystem — AI Infrastructure & Security Research Hub*
