# Phase 3 — Product Opportunity Selection

**Method.** Ten technically feasible concepts were generated against the verified problems
(`01-nigeria-electoral-problem-landscape.md`) and the verified gaps (`02-competitor-landscape.md`), then scored
1–10 on the **official** published criteria and weights (PDF §12 / `00_general_challenge_rules.md`).

**Official weights used (confirmed, not provisional):**

| Criterion | Weight |
|---|---|
| Technical functionality and innovation | 25% |
| Electoral relevance and practical usefulness | 20% |
| Cybersecurity, privacy and responsible AI | 20% |
| Inclusion, accessibility and multilingual capability | 15% |
| Scalability, sustainability and feasibility | 15% |
| Demonstration and documentation | 5% |

Each concept also carries a **red-line risk** rating, because the official rules state that critical
security, privacy, safety or legal concerns **can exclude a project regardless of score**.

---

## 1. The ten concepts

| ID | Concept | One-line description | Primary track |
|---|---|---|---|
| A | **SHAIDA** — Verifiable Electoral Evidence & Triage | Offline-first capture of electoral evidence with cryptographic integrity, deterministic procedural checks that flag (never judge), privacy-preserving multilingual triage, and human adjudication | 5 (+2, +4, +3) |
| B | Provenance-First Official Communications Signer | Tool for electoral bodies/publishers to attach and verify C2PA manifests to official communications | 1 |
| C | Multilingual Claim-Match Bench | Paraphrase-robust multilingual matching of new viral claims to an existing fact-check archive, with harm ranking | 1 |
| D | Results-Sheet Verification Pipeline | EC8A extraction + arithmetic/consistency validation at scale, producing reviewer-ready flags | 2 |
| E | Election Logistics Forecaster | Predict delivery delays and propose staffing on synthetic logistics data | 2 |
| F | Accessibility Mapper | Consent-based crowdsourced reporting of polling-unit venue barriers | 3 |
| G | Retrieval-Restricted Voter Information Assistant | Answers only from an approved corpus, with citation and abstention, in 5 languages | 3 |
| H | Offline Log-Anomaly Monitor | Defensive anomaly detection on synthetic infrastructure logs | 4 |
| I | Impersonation/Phishing Awareness Trainer | Fabricated-example training tool for officials and voters | 4 |
| J | Election-Day Incident Triage | Classify and prioritise citizen incident reports for review | 5 |

---

## 2. Scoring

Scale 1–10 per criterion. Weighted score = Σ(score × weight).

| ID | Tech/Innov (25%) | Relevance (20%) | Cyber/Privacy/RAI (20%) | Inclusion (15%) | Scalability (15%) | Demo (5%) | **Weighted** | Red-line risk |
|---|---|---|---|---|---|---|---|---|
| **A** | **9** | **9** | **10** | **8** | **8** | **9** | **8.85** | **Low** |
| B | 8 | 7 | 9 | 6 | 7 | 8 | 7.65 | Medium (requires publisher adoption) |
| C | 7 | 8 | 7 | 9 | 8 | 7 | 7.70 | Medium (verdict risk on speech) |
| D | 6 | 9 | 7 | 5 | 8 | 6 | 7.05 | **High** (fraud-accusation risk, base-rate fallacy) |
| E | 6 | 6 | 6 | 5 | 7 | 6 | 6.00 | Low |
| F | 5 | 7 | 7 | 9 | 6 | 6 | 6.55 | Medium (disability-data consent) |
| G | 6 | 8 | 6 | 10 | 8 | 6 | 7.20 | **High** (invented electoral rules) |
| H | 6 | 5 | 8 | 4 | 6 | 5 | 5.90 | Low |
| I | 5 | 6 | 8 | 6 | 7 | 6 | 6.25 | Low |
| J | 5 | 8 | 7 | 7 | 7 | 6 | 6.65 | Medium (publishing unverified accusations) |

### Worked calculation for the winner (A)

`9×0.25 + 9×0.20 + 10×0.20 + 8×0.15 + 8×0.15 + 9×0.05`
`= 2.25 + 1.80 + 2.00 + 1.20 + 1.20 + 0.45 = 8.85`

### Runner-up check (C, 7.70) and (B, 7.65)

Concept C scores well but its **red-line risk is Medium**: even a *matching* tool drifts toward labelling
speech, and the official Track 1 brief forbids auto-labelling without human review. Concept B depends on
publisher adoption that a hackathon prototype cannot demonstrate. Neither reaches A's combination of **high
score and low red-line risk**.

---

## 3. Detailed justification for the winner (Concept A — SHAIDA)

**The specific unmet problem.** A citizen, observer or fact-checker captures electoral evidence but cannot
(a) prove it has not been altered, (b) check it against objective public procedural rules, and (c) get it to a
human reviewer with a clear, explainable reason — without the tool declaring a result, accusing a person, or
exposing the reporter. (Evidence: P1, P2, P5, P6, P7, P8, P13 in `01-...`; gap analysis §5 in `02-...`.)

**Existing solutions and their limitations.** IReV shows images but offers no citizen verification primitive
(C1). Situation Room tools are coalition-scale and human-mediated (C2). YIAGA's PVT is sample-level (C3).
Fact-checkers are manual and capacity-bound (C4). Commercial tools are paid, English-first, non-electoral and
verdict-oriented (C5–C8). The saturated classes (C14–C16) are actively discouraged by the briefs.

**Why this is meaningfully different.** It is the only concept that treats **evidence integrity as the core
product**, not a feature: a hash-chained audit log, deterministic procedural checks that emit *flags*,
privacy-by-default capture, and human adjudication — exactly the intersection the official briefs reward
(Track 5 5B/5C + Track 2 2A/2D + Track 4 4B/4D).

**Target users.** Domestic election observers and CSO volunteers; citizen reporters; fact-checkers/newsrooms;
research and accountability groups.

**The AI component and why it is necessary.** Three narrowly-scoped AI tasks, each with an abstention path:
(1) multilingual (en/pcm/ha/yo/ig) claim matching against an archive; (2) harm + check-worthiness ranking to
order a reviewer's queue; (3) plain-language explanation *drafting* of a deterministic flag. AI is necessary
for (1) and (2) because paraphrase-robust multilingual matching at volume is not achievable with string rules;
it is **not** used for (3)'s decision, which stays deterministic.

**Technical feasibility.** Deterministic core (arithmetic, thresholds, hashing, hash chaining) is
straightforward and provable. Matching uses TF-IDF character n-grams with a multilingual token normaliser — no
network dependency, no model download, no API key. Fully offline-capable.

**Data availability.** The official synthetic pack (results, anomalies, incidents, claims, polling units,
FAQ, accessibility survey, logistics) plus self-generated synthetic scenarios. No personal data, no live data.

**Security and privacy risks and mitigations.** Reporter exposure → no identity by default, coarse location,
k-anonymity threshold on aggregation. Tampering → hash chain with verification endpoint. Abuse/flooding →
rate limiting and duplicate detection. Misuse as a fraud oracle → no fraud vocabulary in output; UI copy and
tests enforce it.

**How to demonstrate it.** A two-and-a-half-minute screen recording: a citizen files a report offline; the app
shows the hash and the chain; a tampered record fails verification on camera; the reviewer queue ranks by harm;
a reviewer adjudicates with a reason; the audit log proves the whole sequence.

**How to evaluate it.** Precision/recall/F1 on injected anomalies with a held-out split; base-rate-aware
alert-per-1000 workload; calibration/abstention; paraphrase/typo/code-switch robustness; tamper-detection
tests; k-anonymity tests; axe accessibility audit; API integration and end-to-end tests.

**National relevance.** Directly relevant to 2027 general elections, off-cycle elections, and any
observer/CSO workflow. Composable: any coalition tool can consume the integrity primitive.

**Special-award potential.** Strong fit for **Cybersecurity and Resilience** (hash-chained tamper-evident
audit trail, privacy-preserving reporting) and **Responsible AI and Safety** (abstention, explainability,
human oversight), with credible reach into **Electoral and Civic Inclusion** (multilingual, offline, low-end
device).

---

## 4. Rejected ideas and reasons

| ID | Concept | Why rejected |
|---|---|---|
| B | Provenance-First Official Communications Signer | Depends on institutional publisher adoption that cannot be demonstrated in a prototype; lower inclusion score; a subset of A's capability. |
| C | Multilingual Claim-Match Bench | Strong, but narrower than A and carries the Track 1 red-line risk of labelling speech; A absorbs its best part (matching + triage) inside a safety-first frame. |
| D | Results-Sheet Verification Pipeline | High red-line risk: the brief warns explicitly about fraud accusations and the base-rate fallacy. Even framed as flags, it invites overclaiming. A keeps the deterministic checks but subordinates them to a human-adjudicated evidence record. |
| E | Election Logistics Forecaster | Useful but low differentiation; advisory-only; weak on privacy/RAI narrative; no compelling demo story. |
| F | Accessibility Mapper | Valuable but narrow; disability-data consent risk; a mapping app alone does not demonstrate responsible-AI engineering. |
| G | Retrieval-Restricted Voter Information Assistant | High red-line risk (invented rules); the saturated "chatbot" class; and the brief itself steers away from it. |
| H | Offline Log-Anomaly Monitor | Low electoral relevance and weak inclusion; a component looking for a product. |
| I | Impersonation/Phishing Awareness Trainer | Low innovation; a training deck with a quiz; minimal technical depth. |
| J | Election-Day Incident Triage | Solid, but strictly a subset of A (A adds evidence integrity, provenance and privacy engineering). |

**The hypothesis from Phase 1 was tested, not assumed.** The combination of evidence provenance,
privacy-preserving incident intelligence, procedural verification and accountable human review scored highest
**and** carried the lowest red-line risk — so it was selected on evidence.

---

## 5. Decision

**Selected product: Concept A — SHAIDA — Verifiable Electoral Evidence & Triage.**

- **Name.** SHAIDA (Hausa *shaida* — "evidence / a mark of proof"; verified on Hausa Wiktionary, 2026-11-09).
- **Tagline.** *Prove it happened. Flag it fairly. Let a human decide.*
- **Track.** Primary Track 5, with Track 2, Track 4 and Track 3 capability.
- **Non-negotiable design constraints inherited from the briefs:** no live-system access; synthetic/public
  data only; flags never verdicts; no fraud accusations; no reporter identity by default; offline-first;
  five-language interface; full audit trail; abstention over guessing.
