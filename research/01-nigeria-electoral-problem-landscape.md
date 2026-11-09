# Phase 1 — Nigeria Electoral Problem Landscape

**Purpose:** establish the real, documented problems this project addresses before any code is written.
**Method:** primary/official sources first, then credible Nigerian and international research and journalism.
**Captured:** 2026-11-09.

**Evidence labels used throughout:** `[FACT]` documented with a named source · `[EXPERT]` expert/institutional
opinion · `[HYPOTHESIS]` reasoned inference not yet directly evidenced · `[ASSUMPTION]` a premise this project
relies on that we could not verify.

---

## 0. Source register (33 sources)

| # | Source | Type | Used for |
|---|---|---|---|
| S1 | INEC — https://inecnigeria.org/ | Official institution | Institutional context |
| S2 | INEC IReV portal — https://irev.inecnigeria.org/ | Official institution | Result-viewing architecture |
| S3 | INEC Result Viewing Portal (IReV) — en.wikipedia.org/wiki/INEC_Result_Viewing_Portal | Reference, citing INEC/EU | IReV history, 2023 glitches |
| S4 | Bimodal Voter Accreditation System (BVAS) — en.wikipedia.org/wiki/Bimodal_Voter_Accreditation_System | Reference, citing INEC & Electoral Act 2026 | Accreditation, over-voting rule |
| S5 | 2023 Nigerian presidential election — en.wikipedia.org/wiki/2023_Nigerian_presidential_election | Reference | Turnout, collation, contestation |
| S6 | 2027 Nigerian general election — en.wikipedia.org/wiki/2027_Nigerian_general_election | Reference | Forward-looking context |
| S7 | 2023 Nigerian gubernatorial elections — en.wikipedia.org/wiki/2023_Nigerian_gubernatorial_elections | Reference | Off-cycle dynamics |
| S8 | Elections in Nigeria — en.wikipedia.org/wiki/Elections_in_Nigeria | Reference | Framework |
| S9 | **Electoral Act 2026** (National Assembly of Nigeria, 18 Feb 2026), as cited by S4 | Primary legislation | s.47 (BVAS), s.51 (over-voting) |
| S10 | European Union Election Observation Mission Nigeria 2023 Final Report (via S4 citations; direct PDF blocked 403) | Official observation mission | Observation findings |
| S11 | Premium Times — IReV tag archive — premiumtimesng.com/tag/irev | Investigative journalism | IReV performance, upload failures |
| S12 | YIAGA Africa — yiaga.org (site intermittently 503) & en.wikipedia.org/wiki/YIAGA_Africa | CSO | Parallel vote tabulation, observation scale |
| S13 | Nigeria Civil Society Situation Room — situationroomng.org | CSO coalition | 2027 statements, incident reporting |
| S14 | ICIR — icirnigeria.org | Investigative journalism | Elections/INEC reporting desk |
| S15 | CLEEN Foundation — cleen.org | CSO | Security/accountability |
| S16 | Centre for Democracy and Development (CDD) — cddwestafrica.org | Research org | Fact-checking, governance |
| S17 | Nigeria Data Protection Commission — en.wikipedia.org/wiki/Nigeria_Data_Protection_Commission; ndpc.gov.ng | Regulator | NDPA 2023 context |
| S18 | **NDPA 2023** (Nigeria Data Protection Act) | Primary legislation | Lawful basis, minimisation |
| S19 | ACE Electoral Knowledge Network — aceproject.org | International reference | Electoral integrity frameworks |
| S20 | NDI — ndi.org | International org | Observation methodology |
| S21 | IRI — iri.org | International org | Observation methodology |
| S22 | IFES — ifes.org | International org | Election technology risk |
| S23 | C2PA — c2pa.org; specifications v2.1 | Standards body | Content provenance |
| S24 | Content Credentials — en.wikipedia.org/wiki/Content_Credentials | Reference | Adoption by OpenAI/Google/Meta/Microsoft, YouTube labels |
| S25 | Deepfake — en.wikipedia.org/wiki/Deepfake | Reference | Synthetic media |
| S26 | Disinformation — en.wikipedia.org/wiki/Disinformation | Reference | Coordinated manipulation |
| S27 | Nigerian Pidgin — en.wikipedia.org/wiki/Nigerian_Pidgin | Reference | Language reach |
| S28 | Election monitoring — en.wikipedia.org/wiki/Election_monitoring | Reference | Observation workflow |
| S29 | Rise Networks — risenetworks.org; ai4elections.risenetworks.org | Official programme | Problem framing, tracks |
| S30 | FactCheckHub — factcheckhub.com | Nigerian fact-checking | Claim triage practice |
| S31 | Dubawa — dubawa.org | Nigerian fact-checking | Verification practice |
| S32 | Full Fact — fullfact.org | International fact-checking | Triage/automation lessons |
| S33 | Reality Defender / Truepic / Logically — commercial deepfake & provenance vendors | Commercial prior art | Market gap analysis |

> **Verification note.** Several products named in the mission brief (`everyvotes.org`, `openballot.ng`,
> `ireport.inecnigeria.org`, `steem.ng`, `run-am.com`) resolved to **no DNS record or no HTTP response** on
> 2026-11-09. They are treated as non-operational and are documented as such in
> `research/02-competitor-landscape.md`. Direct fetches of the EU EOM PDF, OHCHR, IFES and NDPC were blocked
> (403); those facts are cited from the secondary sources that quote them, and are marked as such.

---

## 1. The fifteen problem areas

For each: what happens · who experiences it · evidence · frequency/severity · why current approaches fall
short · current workaround · cost of inaction · whether AI genuinely helps · buildability by a small team ·
how to test without live infrastructure.

### P1 — Electoral transparency and accountability

- **What happens.** Voters and civil society cannot reliably trace a polling-unit result from the polling-unit
  result sheet (Form EC8A) through ward, LGA and state collation to the final declaration. The legal process
  of collation is manual and paper-based; the digital record (IReV) is a *viewing* portal, not the collation
  system. `[FACT]` INEC states IReV "is not election result collation system" (S11); IReV is "distinct from the
  legal process of collation and declaration of election winners" (S3).
- **Who.** Voters, journalists, observers, opposition parties, and INEC itself (whose credibility is at stake).
- **Evidence.** In 2023 the results were "cumulated from the polling units manually after failing to upload them
  online through the result viewing portal as assured to the citizens" (S5). The Supreme Court found IReV
  malfunctioning "reduced public confidence in presidential election" (S11).
- **Frequency/severity.** National, once per general-election cycle, with recurring off-cycle instances
  (S7, S11: "IReV uploads stall as 66 polling unit results remain missing").
- **Why insufficient.** IReV shows uploaded images but does not, on its own, let an ordinary citizen
  *systematically verify arithmetic and consistency across the chain* or *preserve an independently verifiable
  record*. There is no widely used citizen-facing tool that turns a pile of result-sheet images into a
  checkable, auditable, tamper-evident ledger of flags.
- **Workaround today.** Manual review by CSOs and newsrooms; ad-hoc spreadsheet work; screenshots.
- **Cost of inaction.** Eroded trust, disputed outcomes, litigation, and violence risk.
- **AI fit.** **Partial and careful.** Deterministic arithmetic/consistency checks are the trustworthy core;
  AI can assist with extraction from messy scans and plain-language explanation of *why* a record was flagged.
- **Buildability.** **High** — the arithmetic rules are public and simple; the hard part is disciplined,
  calibrated, human-in-the-loop design.
- **Testing without live systems.** Fully testable on the official synthetic pack and generated scenarios with
  known injected errors.

### P2 — Polling-unit reporting and result-sheet (EC8A) integrity

- **What happens.** EC8A is filled by hand at the polling unit. Errors arise from illegible handwriting,
  transcription, arithmetic mistakes (votes + rejected ≠ accredited), digit transposition, suspicious round
  numbers, and records duplicated from another unit. `[FACT]` the official synthetic pack models exactly these
  five anomaly types (`accredited_exceeds_registered`, `sum_mismatch`, `digit_transposition`,
  `suspicious_round_numbers`, `duplicated_from_previous_unit`) (S29, `data/synthetic/DATA_DICTIONARY.md`).
- **Who.** Polling officials, collation officers, observers, fact-checkers.
- **Evidence.** Over-voting has explicit legal consequence: under **s.51 of the Electoral Act 2026**, a result
  may be cancelled where votes cast exceed accredited voters (S4, S9). `[FACT]`
- **Frequency/severity.** The official synthetic pack injects **~5%** inconsistencies (S29) — a deliberately
  plausible modelling assumption, not a measured real-world rate `[ASSUMPTION]`.
- **Why insufficient.** Manual collation cannot catch systematic patterns; humans reviewing thousands of sheets
  cannot triage reliably, and an uncalibrated automated checker would produce overwhelming false alarms.
- **Workaround.** Spreadsheet spot-checks; observer samples.
- **Cost of inaction.** Errors propagate upward, and legitimate results get contested on technicalities.
- **AI fit.** **Partial.** Deterministic rules for arithmetic; AI for extraction and explanation only.
- **Buildability.** **High.**
- **Testing.** Injected-anomaly ground truth + held-out labels (official `anomaly_labels_HELD_OUT.csv`).

### P3 — Electronic transmission and result collation

- **What happens.** BVAS captures accreditation and uploads result records to IReV. In 2023, uploads glitched
  and the chain effectively reverted to manual collation. `[FACT]` INEC spokesperson acknowledged upload
  "glitches" (S3); INEC maintains IReV will be used in 2027 (S3).
- **Who.** All voters; INEC; observers.
- **Evidence.** S3, S5, S11 (multiple Premium Times items, incl. Osun 2026 performance analysis and
  "IReV uploads different from results transmission for physical collation").
- **Frequency/severity.** High impact when it occurs; correlates with low-connectivity areas.
- **Why insufficient.** Connectivity, device and process failures are operational; citizens lack a way to
  *independently record what they observed* at the unit.
- **Workaround.** Observers phone in reports; manual tallying.
- **Cost.** Contested legitimacy.
- **AI fit.** **Low** for the transmission itself; **moderate** for classifying/prioritising resulting reports.
- **Buildability.** **High** for an observation-side tool; **never** touch the live system (disqualifying).
- **Testing.** Synthetic logs and reports only.

### P4 — Electoral cybersecurity

- **What happens.** Threat surface includes phishing/impersonation of officials, device compromise, insider
  risk, and infrastructure probing. `[FACT]` the official Track 4 brief lists defensive monitoring, secure
  design, hash-chained tamper-evident logs, RBAC and secrets management as in-scope, and **any** unauthorised
  access as immediately disqualifying (S29).
- **Who.** INEC staff, observers, citizens, and public trust generally.
- **Evidence.** Track 4 scope and STRIDE/LINDDUN guidance (S29); election-technology risk literature (S22).
- **Frequency/severity.** `[HYPOTHESIS]` No public, authoritative, quantified incident rate for Nigeria could be
  verified in this research. We therefore do **not** claim one.
- **Why insufficient.** Awareness and tamper-evidence are under-tooled; privacy-preserving reporting is rare.
- **Workaround.** Manual advisories; after-the-fact incident response.
- **Cost.** Compromise risk and lost trust.
- **AI fit.** **Partial** — phishing-awareness content generation and anomaly triage on synthetic logs.
- **Buildability.** **High** for defensive, offline, synthetic-data tooling.
- **Testing.** Entirely in an isolated local environment with synthetic data.

### P5 — Deepfakes and synthetic political media

- **What happens.** AI-generated or manipulated audio/video/images of officials or candidates circulate
  during campaigns. `[FACT]` deepfake technology and its political misuse are well documented (S25); the
  official Track 1 brief explicitly names "synthetic media, impersonation and misleading content" (S29).
- **Who.** Voters, newsrooms, fact-checkers, candidates, INEC.
- **Evidence.** S25; Track 1 brief (S29); the brief's own guidance is telling — the recommended approach is a
  **"synthetic media screening assistant"** that *"guide[s] users through verification steps … rather than
  issuing a fake/real verdict"* (S29, item 1D).
- **Frequency/severity.** `[EXPERT]` increasing; specific Nigerian rates are not publicly quantified here.
- **Why insufficient.** Binary deepfake detectors are brittle, easily evaded, and produce confident wrong
  answers; they are also inappropriate as a public verdict on someone's speech (Track 1 red line).
- **Workaround.** Manual reverse-image search; journalist judgement.
- **Cost.** Panic, fabricated scandals, and eroded trust in authentic content.
- **AI fit.** **Careful.** Provenance inspection + guided verification + human review is defensible; a bare
  "real/fake" classifier is not, and is discouraged by the official brief.
- **Buildability.** **High** for a provenance/verification workflow; **low** for a reliable universal detector.
- **Testing.** Synthetic, clearly-labelled samples; C2PA-manifest fixtures.

### P6 — Coordinated misinformation and information manipulation

- **What happens.** Viral claims spread on WhatsApp-like channels and social platforms, often in Pidgin and
  other Nigerian languages, mixing true, false, misleading and unverifiable content. `[FACT]` the official
  starter data models exactly four labels (`true`, `false`, `misleading`, `unverifiable`), five channels and a
  `spread_score` (S29). `[FACT]` Nigerian Pidgin is a major lingua franca with very large speaker numbers (S27).
- **Who.** Ordinary voters, fact-checkers (FactCheckHub S30, Dubawa S31), newsrooms.
- **Evidence.** S29, S30, S31, S32; the track brief's emphasis on Pidgin and WhatsApp-like channels.
- **Frequency/severity.** High during campaigns; fact-checker capacity is a hard bottleneck.
- **Why insufficient.** Fact-checkers cannot read everything; the same claim reappears reworded, in another
  language, days later. Matching a *new* claim to an *already fact-checked* one is the highest-leverage
  unsolved step. `[EXPERT]` (Track 1 brief item 1B names exactly this).
- **Workaround.** Manual archive search; institutional memory.
- **Cost.** Slow corrections; repeated debunking; wasted scarce reviewer time.
- **AI fit.** **Strong** — multilingual semantic matching + harm/check-worthiness ranking + abstention.
- **Buildability.** **High.**
- **Testing.** Official `misinformation_claims_synthetic.jsonl` + paraphrase/typo/code-switch augmentation.

### P7 — Election observer workflows

- **What happens.** Observers capture structured, timestamped observations at scale, often offline, then
  report. `[FACT]` YIAGA Africa deployed 3,000 observer teams to 1,500 polling units for the 2019 presidential
  election (S12). Observation methodology is well established (S20, S21, S28).
- **Who.** Domestic observer groups, CSOs, international missions.
- **Evidence.** S12, S28; Track 5 brief items 5A–5C (S29).
- **Frequency/severity.** Every election; workload peaks on election day.
- **Why insufficient.** Paper forms and inconsistent formats; evidence hygiene (timestamps, hashes) is rarely
  automated; reports arrive in floods that cannot be triaged fast enough.
- **Workaround.** Paper checklists, WhatsApp groups, spreadsheets.
- **Cost.** Evidence lost or unverifiable; late insight.
- **AI fit.** **Strong** for triage/prioritisation; **weak** for the reporting itself (must stay deterministic).
- **Buildability.** **High.**
- **Testing.** Official `incident_reports_synthetic.csv` + generated scenarios.

### P8 — Citizen incident reporting and evidence verification

- **What happens.** Citizens want to report problems (queue, logistics, intimidation, malfunction) but
  existing channels are unstructured, unverified, and can expose the reporter. `[FACT]` the Situation Room
  runs citizen reporting infrastructure (S13); the Track 5 brief requires anonymity options, data
  minimisation and deletion, and forbids publishing unverified accusations naming individuals (S29).
- **Who.** Citizens, especially in low-connectivity or high-risk areas.
- **Evidence.** S13, S29.
- **Frequency/severity.** High on election day; risk of harm to reporters is real.
- **Why insufficient.** Free-text reports are unprocessable at volume; there is no built-in evidence hygiene;
  privacy is usually an afterthought.
- **Workaround.** Social media posts; hotlines.
- **Cost.** Unverifiable allegations, mis/disinformation, and reporter risk.
- **AI fit.** **Strong** for triage and de-duplication; **must** be paired with deterministic evidence
  hygiene (hashing, timestamps) and strict privacy defaults.
- **Buildability.** **High.**
- **Testing.** Synthetic reports with known severity/labels.

### P9 — Accessibility for people with disabilities

- **What happens.** Persons with disabilities face venue, information and interface barriers. `[FACT]` the
  official starter data includes a 500-row accessibility-barriers survey with disability type and preferred
  language (S29); Track 3 explicitly requires WCAG 2.2 AA and assistive-interface options.
- **Who.** PWDs, older voters, low-literacy voters.
- **Evidence.** S29 (Track 3 brief, `accessibility_barriers_survey_synthetic.csv`).
- **Frequency/severity.** Systemic and persistent.
- **Why insufficient.** Most civic tech is English-first, text-heavy and not screen-reader-tested.
- **Workaround.** Human assistance; ad-hoc accommodations.
- **Cost.** Direct disenfranchisement.
- **AI fit.** **Moderate** — plain-language rewriting, voice, translation, with human review.
- **Buildability.** **High** for accessible UI; **careful** about AI-generated civic content.
- **Testing.** Automated axe audit + keyboard/screen-reader checks.

### P10 — Multilingual civic and electoral information

- **What happens.** Official information is largely English; many citizens operate in Pidgin, Hausa, Yoruba
  and Igbo. `[FACT]` the official FAQ dataset ships English + Pidgin drafts with **Hausa/Yoruba/Igbo columns
  deliberately empty**, pending native-speaker reviewers (S29).
- **Who.** Voters outside English-dominant audiences.
- **Evidence.** S29, S27.
- **Frequency/severity.** Structural.
- **Why insufficient.** Machine translation of electoral rules risks inventing rules — the Track 3 red line is
  explicit: "No invented electoral rules or dates", with a **zero-unsupported-answers** target.
- **Workaround.** Bilingual volunteers.
- **Cost.** Unequal access to information; susceptibility to rumours.
- **AI fit.** **Moderate**, and only with retrieval restricted to an approved corpus.
- **Buildability.** **High** for retrieval-restricted answering; **low** for free-form generation.
- **Testing.** Answer-accuracy vs approved sources; hallucination counting.

### P11 — Electoral operational failures (logistics)

- **What happens.** Late delivery of materials, incomplete kits, long queues, staff shortfalls. `[FACT]` the
  official starter data includes 300 logistics deliveries with distance, vehicle, dispatch hour, transit hours
  and completeness (S29); 2023 saw documented logistical failures (S5, S10).
- **Who.** Polling officials, voters (waiting hours), INEC.
- **Evidence.** S29, S5, S10.
- **Frequency/severity.** Recurrent.
- **Why insufficient.** Planning is manual; historical failure patterns are not systematically learned.
- **Workaround.** Experience and manual contingency.
- **Cost.** Disenfranchisement of those who cannot wait; credibility loss.
- **AI fit.** **Moderate** — forecasting on synthetic data; strictly advisory.
- **Buildability.** **High.**
- **Testing.** Synthetic logistics data with held-out splits.

### P12 — Voter registration and access to reliable information

- **What happens.** Citizens are unsure how to check registration, collect a PVC, find a polling unit, or
  understand procedures. `[FACT]` the official FAQ dataset covers registration, PVC collection and related
  topics (S29); 93.4M registered voters in 2023 but only 26.71% turnout (S5).
- **Who.** Voters, especially first-time and rural voters.
- **Evidence.** S5, S29.
- **Frequency/severity.** Structural; low turnout is a measurable symptom.
- **Why insufficient.** Information is fragmented across pages and languages; rumour fills the gap.
- **Workaround.** Family, radio, social media.
- **Cost.** Low participation; rumour-driven behaviour.
- **AI fit.** **Moderate** with strict citation and abstention.
- **Buildability.** **High.**
- **Testing.** Answer accuracy vs approved corpus; abstention rate on out-of-corpus questions.

### P13 — Evidence preservation and post-election accountability

- **What happens.** Disputes hinge on evidence that must be preserved, timestamped and shown to be
  unaltered. `[FACT]` Track 4 explicitly suggests "offline-tolerant, tamper-evident audit trails (e.g.
  hash-chained logs)" (item 4D) and Track 5 item 5C suggests timestamps and hashes without exposing
  identities (S29). C2PA/Content Credentials provide a provenance standard already adopted by major
  platforms (S23, S24).
- **Who.** Observers, litigants, journalists, researchers.
- **Evidence.** S23, S24, S29.
- **Frequency/severity.** Critical in every disputed election.
- **Why insufficient.** Evidence is scattered in screenshots and chat threads with no integrity proof.
- **Workaround.** Manual archiving; screenshots.
- **Cost.** Unprovable claims; lost accountability.
- **AI fit.** **Low** — this must be deterministic and cryptographic, not generative.
- **Buildability.** **High** (hash chaining, hashing, signed manifests).
- **Testing.** Tamper tests: mutate a record and prove verification fails.

### P14 — Election-related violence and safe handling of sensitive reports

- **What happens.** Reports may involve intimidation, violence or threats, and careless handling can endanger
  reporters and witnesses. `[FACT]` 2023 saw documented violence (S5); Track 5 red lines forbid location
  precision that endangers observers and default collection of reporter identity (S29).
- **Who.** Reporters, witnesses, observers, communities.
- **Evidence.** S5, S29, S15.
- **Frequency/severity.** High impact; safety-critical.
- **Why insufficient.** Most reporting tools collect everything by default.
- **Workaround.** Anonymous hotlines; trusted intermediaries.
- **Cost.** Harm to people; silencing of witnesses.
- **AI fit.** **Careful** — classification only; never auto-escalation to authorities.
- **Buildability.** **High** if privacy-by-default is the design.
- **Testing.** Privacy tests (no identity stored; coarse location only); severity routing tests.

### P15 — Institutional transparency and public trust

- **What happens.** Trust depends on whether citizens can check the record themselves. `[FACT]` the 2027
  Situation Room statement calls for "fair political competition, institutional independence, transparent
  election management and protection of citizens' democratic rights" (S13). The Supreme Court linked IReV
  malfunction to reduced public confidence (S11).
- **Who.** Everyone.
- **Evidence.** S11, S13, S5.
- **Frequency/severity.** Continuous.
- **Why insufficient.** Transparency tools that produce unverifiable claims can *reduce* trust.
- **Workaround.** Press releases and press coverage.
- **Cost.** Legitimacy deficits.
- **AI fit.** **Indirect** — AI helps only where it increases verifiability without replacing human judgement.
- **Buildability.** **High** for auditable, reproducible checks.
- **Testing.** Reproducibility tests: same input → same output, with a full audit trail.

---

## 2. Cross-cutting findings

1. **The official briefs themselves steer away from the obvious AI answers.** Track 1 item 1D discourages
   fake/real verdicts. Track 2 forbids fraud accusations and warns explicitly about the base-rate fallacy.
   Track 3 demands zero unsupported answers. This is a competition where *restraint and correctness* are the
   differentiator, not model size. `[FACT]`
2. **The rarest, most valuable asset is a trustworthy *chain of evidence*, not another classifier.** Every
   red line in every brief is about not overclaiming. `[EXPERT]`
3. **Human review is a scored requirement, not a courtesy.** It appears in the general rules, in every track
   brief, in the rubric (20% for cybersecurity/privacy/responsible AI) and in the exclusion clause. `[FACT]`
4. **The workload problem is the economic problem.** Fact-checkers and observers are the bottleneck; ranking
   and de-duplication save reviewer time, which is directly measurable ("time-to-triage saved for a
   reviewer (simulated)" is an official success criterion for Track 1). `[FACT]`
5. **Offline-first and low-bandwidth are structural in Nigeria, not edge cases.** `[FACT]` Track 3 and 5 both
   require offline capability; the official polling-unit data includes `network_coverage` with values
   including `none`. `[FACT]`
6. **Provenance standards are now mainstream, and Nigeria is a blank space for them.** OpenAI, Google, Meta
   and Microsoft joined the C2PA steering committee, and YouTube ships "captured with a camera" labels
   (S24). No Nigeria-specific electoral provenance tooling was found in this research. `[HYPOTHESIS]`
   (absence of evidence in our search, not proof of absence).

---

## 3. The convergence: where the unmet need is sharpest

Combining P1, P2, P5, P6, P7, P8 and P13, one unmet need repeats:

> **A citizen, observer or fact-checker can capture or receive a piece of electoral evidence, but has no
> trustworthy, private, offline-capable way to (a) prove the evidence has not been altered, (b) check it
> against objective, public procedural rules, and (c) get it in front of a human reviewer with a clear,
> explainable reason — without the tool ever declaring a result, accusing a person, or exposing the reporter.**

This is precisely the intersection the official briefs reward (Track 5 5B/5C + Track 2 2A/2D + Track 4 4B/4D),
and precisely the space where a small team can build something correct, testable and defensible.

It is taken forward as a **hypothesis** into Phase 3, where it competes against nine other concepts.
