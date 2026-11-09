# SHAIDA — Product definition

> **SHAIDA** · *Hausa: "testimony" / "evidence"*
> Verifiable electoral evidence and human triage.
> One sentence: **SHAIDA lets a citizen, observer or fact-checker lock in what they captured, test
> it against objective public rules, and get it to a human reviewer with a reason — without the
> tool ever declaring a result, accusing a person, or exposing the reporter.**

---

## 1. Problem statement

Nigeria's 2023 general election and the off-cycle elections that followed produced the same
recurring failure, documented across INEC statements, observer reports (Yiaga Africa, the
Nigeria Civil Society Situation Room, EU EOM) and investigative journalism:

- **Evidence exists but cannot be trusted later.** Photos of result sheets, voice notes, incident
  narratives and claims circulate on WhatsApp and X. Nothing binds a copy to the moment it was
  captured. A screenshot cannot prove it was not edited; a hash nobody recorded cannot prove
  anything.
- **The arithmetic that anyone could check by hand is not checked at scale.** EC8A result sheets
  carry the sheet's own internal arithmetic — accredited voters, rejected ballots, per-party
  tallies, the register figure. When those numbers do not close, that is a *deterministic*,
  verifiable contradiction. It is rarely computed systematically before allegations are made.
- **Genuine reports are drowned by volume and by noise.** A CSO running an election-day hotline
  receives thousands of messages, many duplicates, many low-value, a few that matter urgently.
  Human attention is the scarce resource, and it is allocated first-come-first-served rather than
  by harm.
- **Sensitive reports endanger the reporter.** Intimidation, violence and vote-buying reports
  carry a real risk to the person who filed them. Generic reporting tools collect names, phone
  numbers and GPS coordinates by default — exactly the data that can identify and expose them.
- **"AI election tools" overreach.** The most common failure in this space is a tool that
  *declares* — that labels a claim false, a unit fraudulent, a result wrong. That is unsafe,
  legally exposed, and it launders an unaccountable model output into an accusation.

The gap is not more data. It is **provenance, deterministic verification, privacy, and accountable
human review** — in one workflow.

## 2. Target users

| User | Job to be done | What SHAIDA gives them |
|---|---|---|
| **Citizen observer** (primary) | "I saw something. I want it on record, safely, and I want to be able to prove later exactly what I sent." | Offline-capable capture, on-device hashing, no identity collected, coarse location only, a receipt with a hash |
| **Accredited observer / CSO monitor** | "I have hundreds of reports and limited reviewers. Triage by harm, group duplicates, give me an evidence trail." | Harm-ranked queue, duplicate clustering, audit chain, per-finding explanation with innocent explanations listed |
| **Fact-checker / journalist** | "Is this claim I received the same as something already archived and labelled?" | Near-duplicate claim matching against an archive, with prior reviewer labels, multilingual, abstains when unsure |
| **Reviewer (human decision-maker)** | "Tell me why this is at the top and what I should check first." | Published weighted score with every contribution shown, required decision + reason, append-only audit |
| **Election administrator / auditor** | "Can I verify that this record was not altered?" | Public re-verification of the hash chain, arithmetic certificate any observer can re-check |

## 3. Primary user journey (the one flow that must be excellent)

```
Citizen opens SHAIDA (works offline after first load)
   │
   ├─ Picks a category, writes what they saw, optionally attaches a photo
   │     → the photo is SHA-256 hashed ON THE DEVICE before upload
   │     → no name / phone / account field exists anywhere
   │     → precise location is OFF by default; if used, rounded to ~1 km
   │
   ├─ Submits
   │     → receives a receipt: reference id + content hash
   │     → "Keep this. It is how you prove this record was not altered."
   │
   ▼
Report is stored with no identity and linked into an append-only hash chain
   │
   ├─ Deterministic rules run (if it touches a result sheet)
   ├─ Assistive model may suggest a severity — or abstain
   ├─ Near-duplicates cluster into one queue item
   ├─ A transparent weighted score orders it by harm
   │
   ▼
Human reviewer sees a ranked queue
   │
   ├─ Each item shows WHY it ranks where it does, contribution by contribution
   ├─ Each finding lists plausible INNOCENT explanations to rule out first
   ├─ Reviewer records a decision AND a reason (both are required)
   │     → the decision is written to the same audit chain
   │
   ▼
Anyone can re-verify the whole chain from the stored data
```

The journey has one rule: **SHAIDA surfaces questions; a named human answers them.**

## 4. Main differentiator

Most entrants in this space build one of: a chatbot, a misinformation classifier, a results
dashboard, a polling-unit reporting form, or an EC8A OCR tool. Each is a saturated idea, and each
carries the same architectural mistake — the model is the source of truth.

SHAIDA is built on the opposite assumption:

> **The deterministic layer is the source of truth. The AI is only ever allowed to order,
> summarise or suggest — never to conclude.**

This produces four properties that are hard to copy and easy to verify:

1. **Verifiable provenance.** Evidence is hashed before upload; the audit log is a hash chain that
   is re-computed from stored data on every verification. Tampering is *demonstrated* caught by a
   test that edits the database directly (`test_audit_chain_detects_direct_database_tampering`).
2. **Deterministic procedural checks that flag, never judge.** Arithmetic that cannot both be true
   on a correct sheet is computed and shown as a certificate anyone can re-check with a pen. The
   rule engine has **100 % substantiation** — every structural finding's stated contradiction
   actually holds (63/63).
3. **Privacy as architecture, not policy.** There is no field for a reporter's identity. Sensitive
   categories change *handling*, never the verdict. Aggregates are suppressed below a k-anonymity
   floor rather than rounded. Precise coordinates are coarsened before storage.
4. **Accountable human review.** No automated decision exists. Every flag carries a required human
   decision with a mandatory reason, written to the audit chain, and every finding ships with the
   innocent explanations a reviewer should rule out first.

## 5. Core functionality

| # | Capability | Tier | Status |
|---|---|---|---|
| 1 | Report capture with on-device SHA-256 hashing of evidence | deterministic | built |
| 2 | Identity-free storage; coarse location only | deterministic | built |
| 3 | Append-only hash-chained audit log with public re-verification | deterministic | built |
| 4 | Deterministic result-sheet rule engine (7 rules, 2 tiers) | deterministic | built |
| 5 | Arithmetic certificate a reviewer can re-check by hand | deterministic | built |
| 6 | Harm-ranked triage with published weights and per-item explanation | deterministic | built |
| 7 | Near-duplicate incident clustering | deterministic | built |
| 8 | Required human review with mandatory reason, audited | deterministic | built |
| 9 | k-anonymity aggregate suppression | deterministic | built |
| 10 | Multilingual explanations (en, pcm, ha, yo, ig) from fixed templates | deterministic | built |
| 11 | Severity assist (abstaining ordinal model) | assistive | built |
| 12 | Near-duplicate claim matching against an archive | assistive | built |
| 13 | Offline-capable app shell (service worker) | infra | built |
| 14 | Evaluation harness with regression guards | infra | built |

Explicitly **not built**, by design: result declaration, winner projection, fraud
determination, identity collection, live-system access, automated enforcement.

## 6. AI architecture (summary — full detail in `AI-METHODOLOGY.md`)

The architecture is deliberately **inverted** from the usual pattern: the AI is small, optional,
and placed where a wrong answer is harmless.

```
                    ┌──────────────────────────────────────────┐
                    │  DETERMINISTIC CORE  (source of truth)   │
                    │  rules · hash chain · triage weights ·   │
                    │  clustering · k-anonymity · templates    │
                    └──────────────────────────────────────────┘
                                     ▲
        assistive, optional, may abstain │ (never authoritative)
                                     │
        ┌────────────────────────────┴────────────────────────────┐
        │  ASSISTIVE LAYER                                        │
        │  · severity assist  — ordinal model, abstains on a flat  │
        │    posterior; used ONLY to order a queue                 │
        │  · claim matcher    — similarity shortlist + prior label;│
        │    abstains below a floor                                │
        └─────────────────────────────────────────────────────────┘
```

Three hard rules:

1. **No assistive output is ever a finding.** The severity assist orders a queue; it does not
   create a flag. The claim matcher returns candidates with prior labels; it does not label.
2. **Every assistive component can abstain**, and abstention is tested, not assumed.
3. **Explanations are template-filled from deterministic findings**, not generated by a language
   model — so no sentence about someone's evidence can be invented.

## 7. Non-AI deterministic components

- **Rule engine** (`rules.py`): 7 rules in two tiers — structural (arithmetic contradictions:
  R1 accredited > registered, R2 sheet totals do not close, R5 duplicated from previous unit) and
  advisory (statistical hints: R3 adjacent-digit swap, R4 round-number pattern, R6 robust turnout
  outlier via median/MAD, R7 negative/impossible values).
- **Provenance** (`provenance.py`, `storage.py`): canonical JSON hashing, per-record content hash,
  and an append-only hash chain where each entry commits to the previous one.
- **Triage** (`assist.py`): a published weighted sum (severity .35, sensitivity .20, reach .20,
  evidence .10, procedural .10, freshness .05) with a full per-item contribution breakdown.
- **Clustering** (`cluster.py`): deterministic grouping by category + similarity.
- **Privacy floor**: aggregates suppressed entirely below k, never rounded.
- **Templates**: all reviewer and citizen text in five languages, filled with deterministic
  findings only.

## 8. Data architecture (summary — full detail in `TECHNICAL-ARCHITECTURE.md`)

- **SQLite** (`data/shaida.sqlite3`) for reports, audit entries, results, and clusters. Chosen for
  a zero-dependency, single-file, inspectable store that runs anywhere.
- **Official synthetic pack** (`data/official-synthetic/`) loaded read-only as the evaluation and
  demonstration corpus.
- **Evidence files** hashed on ingest; the hash is what is trusted, and it is bound into the audit
  chain.
- **No personal data at rest.** No reporter identity column exists.

## 9. Security model (summary — full detail in `SECURITY-AND-PRIVACY.md`)

- Identity-free by schema, not by policy.
- Hash-chained audit log, verified by re-computation, with direct-DB tampering tests.
- Input validation at the API boundary (Pydantic), stable error shapes that leak nothing.
- Per-client rate limiting against automated abuse.
- No live electoral system is contacted, ever.

## 10. Privacy model

- **Data minimisation:** the minimum needed to review an incident is collected; identity is not.
- **Purpose limitation:** reports are used to route to a human reviewer, nothing else.
- **Storage limitation:** a prototype store, documented as such, with no production retention claim.
- **Location:** off by default; coarsened to ~1 km when used; never returned exactly.
- **Aggregation:** k-anonymity suppression so an individual cannot be recovered by subtraction.
- **NDPA 2023:** the design follows its principles; a formal DPIA is listed as a precondition for
  real use, not claimed as done.

## 11. Human oversight model

- No automated decision path exists. `POST /v1/reports/{id}/review` is the only way a report
  leaves the queue, and it **requires** a decision and a reason.
- Every finding carries plausible innocent explanations to rule out first.
- The API is tested (`test_no_api_response_uses_verdict_language`) so no response can assert a
  verdict.
- The interface states, on every page, that SHAIDA flags and does not judge.

## 12. Evaluation methodology (summary — full detail in `evaluation/`)

- Evaluated against the **organisers' own held-out labels**, not our own.
- Reports two precision numbers where they diverge, and explains why, rather than quoting the
  flattering one.
- Locks measured quality into regression tests.
- Keeps a **rejected heuristic** (49 % over-fire) permanently measured so it cannot return.
- States plainly what the numbers cannot support.

## 13. Deployment architecture

- **Backend:** FastAPI + Uvicorn, SQLite. Single process, no external services, no paid APIs.
- **Frontend:** React + Vite, static build, offline-capable via a service worker that never caches
  API responses.
- **Local:** one command per side; a demo seeder loads synthetic data.
- **Free hosting:** the static frontend can be served from any free static host; the backend runs
  anywhere Python runs. No credential is required to run the prototype.

## 14. Product roadmap

| Phase | Scope | Gate to proceed |
|---|---|---|
| **Prototype (now)** | The 14 capabilities above, on synthetic data | Independent security review; native-speaker review of all non-English strings; accessibility audit with AT users |
| **Pilot (sandbox)** | A single CSO, one state, synthetic or consented data, no production link | DPIA under NDPA 2023; written CSO agreement; ethics review; load and adversarial testing |
| **Supervised operational** | Real observers, real reports, human review only, no public publishing of unverified reports | Signed agreements; incident-response plan; independent audit of the chain; legal review |
| **Widened** | Multi-state, integrations, archival export | Only if every prior gate holds |

Winning the competition does not skip a gate. The About page says so, and the roadmap says so.

---

## Appendix — the design constitution gate (Design Constitution §2)

**Three most important design weaknesses in the pre-existing state:** *(this is a greenfield
prototype, so these are the weaknesses a naive build would have)*

1. An "election AI" tool that declares verdicts, which is unsafe and dishonest.
2. A generic dashboard that shows charts without an operational decision attached.
3. A reporting form that collects identity by default and endangers the reporter.

**Visual direction (one line):** An *evidentiary document*, not a dashboard — paper-toned,
monospace-labelled, structural rules instead of cards, a single amber accent reserved exclusively
for "a human must look at this", and generous type set for reading. It should be remembered as
*the election tool that refused to give a verdict.*
