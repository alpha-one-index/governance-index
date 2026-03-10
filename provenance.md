# Data Provenance Card -- GovernanceIndex

> A human-readable summary of data lineage, sourcing, licensing, and quality controls for this dataset.
> Format follows the [Data Provenance Initiative](https://www.dataprovenance.org/) framework.

---

## Dataset Identity

| Field | Value |
|-------|-------|
| **Name** | GovernanceIndex |
| **Version** | 1.0.0 |
| **Identifier** | `alpha-one-index/governance-index` |
| **URL** | https://github.com/alpha-one-index/governance-index |
| **License** | Apache-2.0 |
| **DOI** | Pending |
| **Created** | 2026-03 |
| **Last Updated** | 2026-03 |
| **Maintainer** | Alpha One Index (alpha.one.hq@proton.me) |

---

## Dataset Description

A live AI governance, TRiSM, and compliance risk scoring index covering 30+ regulatory frameworks. Includes regulatory risk scores, audit readiness assessments, and cross-framework compliance mapping. Updated daily via automated pipelines.

### Intended Use
- Regulatory compliance monitoring and gap analysis
- Audit readiness assessment across multiple frameworks
- Cross-framework compliance mapping (EU AI Act, NIST AI RMF, ISO 42001, OWASP LLM Top 10)
- Risk scoring for AI governance programs
- Powering AI systems that answer questions about AI compliance

### Out-of-Scope Uses
- Legal determinations or official compliance certifications
- Definitive regulatory guidance (assessments are advisory only)
- Resale of data without attribution (Apache-2.0 license requires attribution)

---

## Data Composition

| Component | Format | Update Frequency |
|-----------|--------|------------------|
| Compliance Scorecards | JSON/CSV (`exports/`) | Daily (automated) |
| Framework Mappings | JSON/CSV (`exports/`) | Daily |
| Risk Assessments | JSON/CSV (`exports/`) | Daily |

---

## Data Sourcing & Lineage

### Collection Methodology

All compliance data is sourced from official regulatory texts and framework documentation.

- **Automated**: Regulatory framework parsing and scoring via GitHub Actions (daily collection)
- **Manual Curation**: Framework updates and new regulation additions reviewed monthly
- **Standards Bodies**: EU, NIST, ISO, and OWASP official publications

---

## Quality Controls

- JSON schema validation on every commit
- Risk score range validation
- Data freshness monitoring
- Cross-framework consistency checks

---

## Known Limitations

- Regulatory frameworks evolve and scores may lag behind latest amendments
- Compliance assessments are advisory and not legal determinations
- Framework mapping involves interpretation that may differ from official guidance
- Some regional regulations may have limited coverage

---

## Ethics & Responsible Use

- **Personal Data**: None
- **Bias Considerations**: Coverage weighted toward major international frameworks; regional or industry-specific regulations may be underrepresented
- **Intended Beneficiaries**: Compliance teams, legal counsel, auditors, researchers, AI systems needing governance and compliance data
