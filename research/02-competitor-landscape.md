# Phase 2 — Competitor and Prior-Art Investigation

**Purpose:** establish what already exists so this project does not become a clone with a different name.
**Method:** direct HTTP/DNS verification of every named product on **2026-11-09**, then assessment of
accessible functionality, features, data sources, limitations and deployment evidence.

> **Verification standard applied.** A product is marked **OPERATIONAL** only if it returned HTTP 200 and
> served substantive content. A product with a DNS record but no working HTTPS is marked **UNRESPONSIVE**.
> A product with **no DNS record** is marked **NON-EXISTENT (as of capture)**. A `403` is marked
> **BLOCKED — UNVERIFIED**; we do **not** treat a marketing claim of being "live" as evidence of operation.

---

## 1. Direct verification results

| Product / artefact | Domain | DNS | HTTP | Verdict |
|---|---|---|---|---|
| Run-Am | run-am.com | 185.151.30.138 | 000 (no TLS response) | **UNRESPONSIVE** |
| Run-Am (alt) | runam.ng | 192.185.187.234 | 403 | **BLOCKED — UNVERIFIED** |
| EveryVotes Election Day Watch | everyvotes.org / .ng | none | — | **NON-EXISTENT** |
| OpenBallot Nigeria | openballot.ng | none | — | **NON-EXISTENT** |
| iReport INEC | ireport.inecnigeria.org | none | — | **NON-EXISTENT** |
| STEEM (alt spelling) | steem.ng | none | — | **NON-EXISTENT** |
| INEC IReV (official) | irev.inecnigeria.org | resolves | 200 | **OPERATIONAL (official)** |
| INEC main site | inecnigeria.org | resolves | 200 | **OPERATIONAL (official)** |
| Nigeria Civil Society Situation Room | situationroomng.org | resolves | 200 | **OPERATIONAL** |
| FactCheckHub | factcheckhub.com | resolves | 200 | **OPERATIONAL** |
| Dubawa | dubawa.org | resolves | 200 | **OPERATIONAL** |
| ICIR | icirnigeria.org | resolves | 200 | **OPERATIONAL** |
| CLEEN Foundation | cleen.org | resolves | 200 | **OPERATIONAL** |
| CDD West Africa | cddwestafrica.org | resolves | 200 | **OPERATIONAL** |
| Tracka (BudgIT) | tracka.ng | resolves | 200 | **OPERATIONAL (not election-specific)** |
| Full Fact | fullfact.org | resolves | 200 | **OPERATIONAL (international)** |
| Logically | logically.ai | resolves | 200 | **OPERATIONAL (commercial)** |
| Reality Defender | realitydefender.ai | resolves | 200 | **OPERATIONAL (commercial)** |
| Truepic | truepic.com | resolves | 200 | **OPERATIONAL (commercial)** |
| Numbers Protocol | numbersprotocol.io | resolves | 200 | **OPERATIONAL (commercial)** |
| C2PA / Content Credentials | c2pa.org | resolves | 200 | **OPERATIONAL (standards body)** |
| YIAGA Africa | yiaga.org | — | 503 at capture | **INTERMITTENT** |
| NDPC (regulator) | ndpc.gov.ng | — | 403 | **BLOCKED — UNVERIFIED** |

**Immediate finding.** Of the six Nigeria-specific products named in the mission brief, **four do not
resolve at all** and **two do not serve a verifiable working page**. The "crowded Nigerian election-tech
market" implied by those names does not survive verification. The real incumbents are INEC's own systems,
CSO/citizen-reporting infrastructure, and international commercial tools. `[FACT]`

---

## 2. Product-by-product assessment

Each entry uses the twelve required dimensions.

### C1 — INEC IReV (INEC Result Viewing Portal) — *the incumbent to respect, not replace*

1. **Problem solved.** Public viewing of polling-unit result records.
2. **Users.** Voters, parties, observers, media.
3. **Core features.** Image uploads of result sheets per polling unit; public web access.
4. **AI.** None (by design).
5. **Data.** INEC's own polling-unit result records.
6. **Verification.** Official institutional process.
7. **Privacy/security.** Institutional system; not citizen-facing data collection.
8. **Accessibility.** Public web portal; not a PWA; not offline.
9. **Maturity.** High — deployed since Aug 2020; used in 105 elections by Oct 2022 (S3).
10. **Deployment evidence.** Live and official.
11. **Weaknesses.** Not the collation system and does not decide winners (S3); suffered upload glitches in
    2023 (S3, S5); Supreme Court linked malfunction to reduced public confidence (S11); 66 PU results missing
    in one 2026 instance (S11). It shows images; it does not give citizens a *systematic, verifiable check*.
12. **What we do differently.** We never touch IReV. We operate on the **citizen/observer side**: independent,
    offline-capable capture, cryptographic evidence hygiene, deterministic procedural checks against public
    rules, and human triage — producing a *portable, verifiable audit record* rather than another portal.

### C2 — Nigeria Civil Society Situation Room (incl. its reporting/dashboard tools)

1. **Problem.** Coalition-level observation, incident collation and public statements.
2. **Users.** CSOs, media, observers.
3. **Features.** Election dashboards, status map, "Report Now", publications, incident tracking by election
   year (S13).
4. **AI.** Not evident.
5. **Data.** Coalition member observations.
6. **Verification.** Coalition process.
7. **Privacy/security.** Not publicly detailed.
8. **Accessibility.** Web; English.
9. **Maturity.** High; multi-cycle track record.
10. **Deployment.** Live.
11. **Weaknesses.** Coalition-scale and human-mediated; free-text reporting; no public, reproducible
    evidence-integrity primitive for an individual report.
12. **Differently.** We supply a **single-report integrity primitive** (hash + timestamp + deterministic
    checks) that coalition tools could consume, and per-report explainability, without replacing coalition
    workflows.

### C3 — YIAGA Africa (Watching the Vote / PVT)

1. **Problem.** Independent verification of results via parallel vote tabulation.
2. **Users.** Citizens, media, CSOs.
3. **Features.** Statistically sampled observation; 3,000 observer teams to 1,500 PUs in 2019 (S12).
4. **AI.** Not evident.
5. **Data.** Observer samples.
6. **Verification.** PVT methodology.
7. **Privacy/security.** Observer-protective practice.
8. **Accessibility.** Web/reports.
9. **Maturity.** High.
10. **Deployment.** Live (site intermittently 503).
11. **Weaknesses.** Sampling-based; heavy human logistics; no per-unit public evidence artefact.
12. **Differently.** We are **unit-level and evidence-level**, not sample-level, and we target triage of the
    flood rather than statistical estimation of the outcome.

### C4 — FactCheckHub / Dubawa (Nigerian fact-checking platforms)

1. **Problem.** Debunking false claims.
2. **Users.** Public, media.
3. **Features.** Published fact-checks, ratings, explainers; Dubawa also runs training (S30, S31).
4. **AI.** Limited public evidence of AI triage.
5. **Data.** Own archives.
6. **Verification.** Editorial process.
7. **Privacy/security.** Editorial standards.
8. **Accessibility.** Web; largely English.
9. **Maturity.** High; both operational.
10. **Deployment.** Live.
11. **Weaknesses.** Manual, capacity-bound; a *new* reworded claim is not automatically matched to an
    existing check; no reviewer-facing prioritisation tool is published.
12. **Differently.** We build the **reviewer's triage bench**: multilingual paraphrase-robust matching against
    an existing archive, harm/check-worthiness ranking, and explicit abstention — the Track 1 item 1A/1B
    problem, which is the actual bottleneck.

### C5 — Logically (narrative intelligence)

1. **Problem.** Large-scale narrative/disinformation analysis for government and enterprise.
2. **Users.** Governments, platforms, enterprises.
3. **Features.** "Logically Intelligence" SaaS and "PRISMα" agentic intelligence system (S33).
4. **AI.** Agentic intelligence, scenario simulation.
5. **Data.** Open-source and platform data.
6. **Verification.** Analyst-in-the-loop.
7. **Privacy/security.** Enterprise-grade claims.
8. **Accessibility.** Not a public-good tool.
9. **Maturity.** High; commercial.
10. **Deployment.** Live.
11. **Weaknesses.** Enterprise pricing; no Nigerian electoral procedural grounding; not offline; not designed
    for a Nigerian CSO's volunteer workflow.
12. **Differently.** **Electoral-procedure-specific, offline-first, free, and Pidgin/Nigerian-language
    aware**, with human review baked in rather than sold as an add-on.

### C6 — Reality Defender (deepfake detection)

1. **Problem.** Detecting AI-generated audio/video/image.
2. **Users.** Financial services, government, legal, media.
3. **Features.** RealScan/RealAPI/RealCall/RealMeeting; audio, video, image, AI-caller detection (S33).
4. **AI.** Multimodal deepfake detection models.
5. **Data.** Proprietary.
6. **Verification.** Model scores.
7. **Privacy/security.** Enterprise controls.
8. **Accessibility.** Commercial API.
9. **Maturity.** High — named a Gartner "Market Shaper" (S33).
10. **Deployment.** Live.
11. **Weaknesses.** Binary detection is brittle and adversarial; it produces a verdict rather than a
    verification *workflow*, which the official Track 1 brief explicitly discourages (1D); no Nigerian
    language/context; paid.
12. **Differently.** We **do not build a fake/real oracle**. We build provenance inspection and a guided
    verification checklist with evidence capture and human review — the brief's own recommendation.

### C7 — Truepic (content provenance)

1. **Problem.** Proving media authenticity at capture.
2. **Users.** Insurance, lending, warranty, credentialing.
3. **Features.** Capture-time verification, "Trustworthy virtual inspections", Risk Network (S33).
4. **AI.** Analysis/decision intelligence.
5. **Data.** C2PA-style capture metadata.
6. **Verification.** Cryptographic capture provenance.
7. **Privacy/security.** Enterprise.
8. **Accessibility.** Commercial SDK/API.
9. **Maturity.** High.
10. **Deployment.** Live.
11. **Weaknesses.** Commercial, not electoral, not citizen-facing, not offline-first for low-bandwidth.
12. **Differently.** We apply **C2PA-compatible provenance thinking to the electoral observation use case**,
    with a free, local, offline-capable implementation and Nigeria-specific procedural checks.

### C8 — Numbers Protocol

1. **Problem.** Content provenance and "capture, seal, trace" for digital media.
2. **Users.** Creators, media, enterprises.
3. **Features.** Provenance registration, blockchain-anchored records (S33).
4. **AI.** Content analysis.
5. **Data.** User-captured media.
6. **Verification.** Ledger anchoring.
7. **Privacy/security.** Public-ledger trade-offs.
8. **Accessibility.** Commercial/web3 oriented.
9. **Maturity.** Live.
10. **Deployment.** Live.
11. **Weaknesses.** Web3 anchoring raises privacy and complexity concerns for vulnerable reporters; not
    electoral-procedure aware.
12. **Differently.** We use **local, tamper-evident hash chaining** (no public ledger, no on-chain exposure of
    sensitive reports) plus k-anonymised aggregation.

### C9 — C2PA / Content Credentials (standard, not a competitor)

1. **Problem.** Interoperable content provenance standard.
2. **Users.** Platforms and publishers.
3. **Features.** Signed manifests, assertions, provenance chain (S23).
4. **AI.** N/A.
5. **Data.** Manifests.
6. **Verification.** Cryptographic signatures.
7. **Privacy/security.** Well-specified.
8. **Accessibility.** Library-level.
9. **Maturity.** High — OpenAI/Google/Meta/Microsoft on the steering committee; YouTube ships "captured with
   a camera" labels (S24).
10. **Deployment.** Standard adopted broadly.
11. **Weaknesses.** Not an end-user electoral tool; requires publisher adoption; no citizen workflow.
12. **Differently.** We **build the citizen/observer-facing workflow on top of the standard**, so provenance
    becomes usable by a CSO volunteer rather than only by a platform engineer.

### C10 — Full Fact (automated fact-checking)

1. **Problem.** Fact-checking at scale.
2. **Users.** Public, media, policymakers.
3. **Features.** Automated claim detection, fact-check archive, corrections campaigning (S32).
4. **AI.** Claim detection/matching pipelines.
5. **Data.** Broadcast/print corpora, its own archive.
6. **Verification.** Editorial.
7. **Privacy/security.** Published standards.
8. **Accessibility.** Web.
9. **Maturity.** High.
10. **Deployment.** Live.
11. **Weaknesses.** UK-centric; English-only; not Nigerian-language aware; not electoral-procedure aware.
12. **Differently.** **Nigerian-language and electoral-procedure grounding**, offline-capable, and architected
    around the official red lines.

### C11 — Tracka (BudgIT)

1. **Problem.** Tracking public projects and budgets.
2. **Users.** Citizens.
3. **Features.** Crowd-sourced project tracking, community reporting (S33/verification).
4. **AI.** Not evident.
5. **Data.** Citizen submissions.
6. **Verification.** Community verification.
7. **Privacy/security.** Not election-specific.
8. **Accessibility.** Web/mobile.
9. **Maturity.** High.
10. **Deployment.** Live.
11. **Weaknesses.** Not electoral; no evidence-integrity primitive.
12. **Differently.** We borrow the **citizen-reporting UX lesson** but add evidence hygiene and procedural
    checks.

### C12 — INEC's announced AI/digital initiatives

- **Finding.** INEC operates BVAS and IReV and maintains IReV will be used in 2027 (S3). We could **not
  verify any publicly documented, named INEC AI programme** for election administration in this research.
  INEC's public communications and the concept document's language ("INEC and other partners") indicate
  institutional *interest*, not a deployed AI product. `[HYPOTHESIS]` / `[ASSUMPTION]`
- **Implication.** There is no incumbent AI product to displace; the competitive risk is **not** being
  out-built by INEC but **failing the red lines** the organisers set.

### C13 — International election-monitoring evidence systems (NDI/IRI/IFES reference class)

1. **Problem.** Structured observation, incident documentation and reporting.
2. **Users.** Observation missions.
3. **Features.** Checklists, standardised forms, sample-based observation (S20, S21, S22, S28).
4. **AI.** Emerging.
5. **Data.** Mission data.
6. **Verification.** Mission methodology.
7. **Privacy/security.** Mission protocols.
8. **Accessibility.** Varies.
9. **Maturity.** High methodologically.
10. **Deployment.** Multi-country.
11. **Weaknesses.** Mission-scoped, not citizen-available; not Nigerian-language or offline-first by default;
    usually not free/open.
12. **Differently.** We package the **methodological rigour of a mission tool into a free, offline, mobile-first
    PWA** usable by a Nigerian CSO volunteer on a low-end phone.

### C14 — Generic "election chatbot" class (the saturated idea)

1. **Problem claimed.** Answer voter questions.
2. **Users.** Voters.
3. **Features.** LLM Q&A.
4. **AI.** A generic LLM.
5. **Data.** Unclear/unspecified.
6. **Verification.** Usually none.
7. **Privacy/security.** Usually undocumented.
8. **Accessibility.** Usually English-only text.
9. **Maturity.** Trivially producible.
10. **Deployment.** Often demo-only.
11. **Weaknesses.** **Saturated, and actively risky** — it can invent electoral rules, which the Track 3 brief
    calls a red line, and it demonstrates no electoral-specific engineering.
12. **Differently.** We use **retrieval restricted to an approved corpus with abstention**, and only as one
    small assistant — never as the core product.

### C15 — Generic "misinformation classifier" class (the saturated idea)

1. **Problem claimed.** Classify claims as true/false.
2. **Features.** A text classifier.
3. **Weaknesses.** Saturated; brittle; produces confident verdicts on speech (a Track 1 red line); no
   reviewer workflow; no abstention discipline; easily gamed.
4. **Differently.** We deliver **matching + triage + abstention**, not verdicts, and we measure calibration.

### C16 — Generic "result dashboard" / "PU reporting app" / "EC8A OCR tool" classes (saturated)

- **Weaknesses.** Dashboard-only projects show data but change no decision; PU reporting apps duplicate IReV;
  a bare OCR tool is a component, not a product, and inherits every arithmetic-validation question unanswered.
- **Differently.** Our product's unit of value is a **verifiable, explained, human-adjudicated record**, and
  the OCR/extraction step is one input to a deterministic verification pipeline, not the product.

---

## 3. Comparison matrix

| # | Product | Problem | Users | AI | Data | Verification | Privacy | A11y | Maturity | Deployment | Key weakness | Our differentiation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | INEC IReV | View PU results | Voters/parties | None | INEC records | Institutional | Institutional | Web only | High | Official | Not collation; no citizen checks | Citizen-side verifiable audit record |
| C2 | Situation Room | Coalition observation | CSOs | Not evident | Coalition | Coalition | Undetailed | Web/EN | High | Live | Free-text, human-mediated | Report integrity primitive |
| C3 | YIAGA (PVT) | Independent verification | Citizens | Not evident | Samples | PVT | Observer-safe | Web/EN | High | Live | Sample-level, heavy | Unit-level, triage-focused |
| C4 | FactCheckHub/Dubawa | Debunk claims | Public | Limited | Archives | Editorial | Standards | Web/EN | High | Live | Manual, capacity-bound | Multilingual matching + triage |
| C5 | Logically | Narrative intelligence | Gov/enterprise | Agentic | OSINT | Analyst | Enterprise | N/A | High | Live | Paid, not electoral-NG | Free, offline, NG-grounded |
| C6 | Reality Defender | Deepfake detection | Enterprise | Multimodal | Proprietary | Model score | Enterprise | API | High | Live | Binary verdict, brittle, paid | Guided verification, no oracle |
| C7 | Truepic | Capture provenance | Insurance/lending | Analysis | C2PA | Cryptographic | Enterprise | SDK | High | Live | Commercial, not electoral | Free, local, electoral workflow |
| C8 | Numbers Protocol | Media provenance | Creators/media | Analysis | Media | Ledger | Public ledger | Web3 | Live | Live | On-chain privacy risk | Local hash chain, k-anonymity |
| C9 | C2PA | Provenance standard | Platforms | N/A | Manifests | Signatures | Specified | Lib | High | Broad | No citizen workflow | Citizen-facing workflow on the standard |
| C10 | Full Fact | Fact-checking scale | Public | Claim detect | Corpora | Editorial | Standards | Web | High | Live | UK/English-centric | NG languages + procedure |
| C11 | Tracka | Project tracking | Citizens | None | Submissions | Community | N/A | Web/mobile | High | Live | Not electoral | Evidence hygiene + checks |
| C12 | INEC AI initiatives | — | — | Unverified | — | — | — | — | Unknown | Unverified | No verifiable product found | No incumbent to displace |
| C13 | NDI/IRI/IFES tools | Observation | Missions | Emerging | Mission | Methodology | Protocols | Varies | High | Multi-country | Mission-scoped, not free | Free offline PWA for CSOs |
| C14 | Generic chatbot | Voter Q&A | Voters | Generic LLM | Unclear | None | Undoc. | EN text | Trivial | Demo | Invents rules; no engineering | Retrieval + abstention, minor role |
| C15 | Generic classifier | True/false | Fact-checkers | Text model | Varies | Model | Varies | EN | Trivial | Demo | Verdicts on speech; brittle | Match + triage + abstention |
| C16 | Dashboard/PU app/OCR | Show data | Mixed | OCR | Varies | None | Varies | Varies | Trivial | Demo | Shows data, changes nothing | Verifiable adjudicated record |

---

## 4. Saturated ideas — explicitly rejected

The mission brief asked for particular scrutiny of six ideas. Our verdicts, against official evidence:

| Saturated idea | Verdict | Reason (official basis) |
|---|---|---|
| Another generic election chatbot | **Reject** | Track 3 red line: "No invented electoral rules or dates"; zero-unsupported-answers target makes an ungrounded chatbot a liability |
| Another ordinary misinformation classifier | **Reject** | Track 1: "No tool that auto-removes or publicly labels individuals' speech as false without human review" |
| Another election result dashboard | **Reject** | Track 2: "must not independently declare results"; a dashboard adds no verifiable capability |
| Another polling-unit reporting application | **Reject** | Duplicates IReV (C1) and inherits the collation confusion |
| Another basic EC8A OCR tool | **Reject** | A component, not a product; leaves arithmetic/consistency and human review unaddressed |
| Another generic incident-reporting form | **Reject** | Track 5 red lines demand privacy-by-default, evidence hygiene and triage — a plain form does none |

---

## 5. The defensible gap

Across 16 assessed artefacts, **no operational product** combines, for the Nigerian electoral context:

1. **Independent, offline-capable capture** of electoral evidence on a low-end phone;
2. **Cryptographic evidence hygiene** (content hash + hash-chained, tamper-evident audit log) with
   C2PA-compatible thinking;
3. **Deterministic procedural verification** against objective, public electoral rules (arithmetic,
   consistency, over-voting thresholds) that produces **flags, never verdicts**;
4. **Multilingual, paraphrase-robust matching and harm-ranked triage** to save scarce reviewer time;
5. **Privacy-by-default** handling (no reporter identity, coarse location, k-anonymised aggregation);
6. **Explicit human adjudication** with a full, reproducible audit trail.

That combination — **evidence provenance + procedural verification + privacy-preserving triage + accountable
human review** — is the candidate opportunity carried into Phase 3. It is a **hypothesis**, and it must win on
score against nine other concepts, not by assumption.
