# Technical architecture

## 1. Overview

SHAIDA is a two-tier system with a deliberate asymmetry: a **deterministic core** that is the
source of truth, and a small **assistive layer** that may only order, shortlist or suggest — never
conclude. The architecture exists to make that asymmetry enforceable and testable, not just
stated.

```
┌──────────────────────────────────────────────────────────────────────────┐
│  FRONTEND  ·  React + Vite  ·  static build  ·  offline-capable          │
│  ReportPage · QueuePage · ResultsPage · ClaimsPage · IntegrityPage ·      │
│  AboutPage                                                                │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │  fetch  /v1/*   (never cached by the SW)
┌───────────────────────────────▼──────────────────────────────────────────┐
│  API  ·  FastAPI + Uvicorn  ·  18 endpoints  ·  Pydantic validation       │
│  rate limiting · stable error shapes · no verdict language                │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────┐
│  SERVICE LAYER  ·  service.py  — orchestrates ingest → rules → triage     │
└───────┬─────────────────┬──────────────────┬───────────────────┬──────────┘
        │                 │                  │                   │
   ┌────▼────┐      ┌─────▼─────┐      ┌─────▼─────┐      ┌──────▼──────┐
   │ rules   │      │ provenance│      │  assist   │      │  cluster    │
   │ 7 rules │      │ hash+chain│      │ severity  │      │ deterministic│
   │ 2 tiers │      │ verify    │      │ matcher   │      │ grouping    │
   └─────────┘      └───────────┘      └───────────┘      └─────────────┘
        │                 │                  │                   │
┌───────▼─────────────────▼──────────────────▼───────────────────▼──────────┐
│  STORAGE  ·  SQLite  ·  audit_log · reports · review_actions ·             │
│  result_records                                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

## 2. Repository layout

```
project/
├── backend/
│   ├── shdaida/
│   │   ├── api.py          18 HTTP endpoints, validation, rate limiting
│   │   ├── service.py      orchestration of ingest, rules, triage, review
│   │   ├── rules.py        deterministic rule engine (7 rules, 2 tiers)
│   │   ├── provenance.py   canonical hashing + hash-chain build/verify
│   │   ├── storage.py      SQLite schema + append-only audit + tamper checks
│   │   ├── assist.py       assistive severity model + claim matcher + triage weights
│   │   ├── cluster.py      deterministic incident clustering
│   │   ├── text.py         multilingual normalisation (en/pcm/ha/yo/ig aware)
│   │   ├── taxonomy.py     categories, sensitivity classes, languages
│   │   ├── datasets.py     loader for the official synthetic pack
│   │   └── config.py       settings, validated at startup
│   ├── tests/              6 modules, 111 tests
│   └── requirements.txt
├── frontend/
│   ├── src/pages/          6 page components
│   ├── src/lib/            api client + shared UI primitives
│   ├── src/styles/         tokens.css + app.css (design system)
│   └── public/sw.js        service worker (static assets only)
├── data/
│   ├── official-synthetic/ organisers' starter pack (read-only)
│   ├── evidence/           hashed evidence blobs
│   └── shaida.sqlite3      application store
├── evaluation/             harness, methodology, results, test cases
├── research/               Phase 0–3 research documents
├── docs/                   product, architecture, security, AI, competition docs
├── demo/                   storyboard, narration, video
└── scripts/seed_demo.py    synthetic demo seeder
```

## 3. Data model

### 3.1 `reports` — an incident as filed

| Column | Notes |
|---|---|
| `id` | server-assigned reference (`rep-…`), not a reporter id |
| `category`, `narrative`, `state`, `lga`, `ward`, `pu_id` | what was observed |
| `reporter_type` | role only (`citizen`/`observer`/`party_agent`/`official`) — **not identity** |
| `severity_reported` | optional; may be absent, in which case the assist may suggest one |
| `latitude`, `longitude` | optional, coarsened to ~1 km before storage |
| `evidence_hash` | SHA-256 of the evidence file, computed on the client |
| `content_hash` | SHA-256 over the canonical report payload |
| `priority` | deterministic weighted score |
| `is_sensitive` | derived from category; changes handling, never the verdict |
| `created_at` | timestamp |

There is **no** column for a name, phone number, email, account or IP address. Identity-free is a
schema property, and `test_no_reporter_identity_is_stored` asserts it.

### 3.2 `audit_log` — append-only hash chain

| Column | Notes |
|---|---|
| `seq` | monotonic sequence; bound inside the hash |
| `action` | `report.created`, `report.reviewed`, … |
| `subject` | what the action concerns |
| `actor` | `reporter` or a reviewer handle — never a private individual's name |
| `payload` | the canonical payload that was committed |
| `payload_hash` | SHA-256 of `payload` |
| `prev_chain_hash`, `chain_hash` | the chain link |

`chain_hash = SHA256(prev_chain_hash ‖ payload_hash ‖ seq)`.

**Tamper-evidence is verified by re-computation, not by trust.** `storage.audit_chain()`
re-hashes the *stored payload* rather than trusting the stored digest, then walks the chain. If a
row is edited directly in SQLite, the recomputed digest no longer matches and verification fails
and names the row. Three tests prove it: `test_audit_chain_detects_direct_database_tampering`,
`test_audit_chain_detects_row_deletion`, and the chain-level
`test_chain_detects_reordering`.

> **Hard-won note.** An earlier version trusted the stored `payload_hash`. That is a real
> vulnerability: editing the payload *and* its digest together would pass verification. The fix
> was to re-hash the payload from scratch. This is recorded because it is exactly the kind of
> subtle flaw that a "tamper-evident" claim invites.

### 3.3 `result_records` — polling-unit returns

| Column | Notes |
|---|---|
| `pu_id` | unit identifier |
| `registered`, `accredited`, `rejected` | sheet figures |
| `votes` | per-party tallies |
| `findings` | JSON array of deterministic findings with tier + message + certificate |
| `content_hash` | canonical hash of the record |

### 3.4 `review_actions` — human decisions

| Column | Notes |
|---|---|
| `report_id` | the report reviewed |
| `decision` | constrained enum |
| `reason` | **required** — the API rejects a review without one |
| `reviewer` | handle |
| `created_at` | timestamp |

## 4. API surface (18 endpoints)

| Method | Path | Purpose |
|---|---|---|
| GET | `/v1/health` | liveness; declares no verdict capability |
| GET | `/v1/stats` | counts, assist availability, dataset sizes |
| GET | `/v1/datasets` | which datasets are loaded |
| POST | `/v1/reports` | file a report; returns reference + hashes |
| GET | `/v1/reports` | list, filterable, harm-ordered |
| GET | `/v1/reports/{id}` | one report |
| GET | `/v1/reports/{id}/verify` | verify the record's content hash |
| GET | `/v1/reports/{id}/explain` | per-signal explanation, in a chosen language |
| POST | `/v1/reports/{id}/review` | record a human decision (**reason required**) |
| POST | `/v1/results/check` | run the rule engine over a batch of records |
| POST | `/v1/results/load-official` | load the official synthetic pack |
| GET | `/v1/results` | list checked records |
| GET | `/v1/results/{pu_id}` | one record with findings |
| GET | `/v1/results/{pu_id}/certificate` | arithmetic certificate |
| POST | `/v1/claims/match` | near-duplicate claim shortlist |
| GET | `/v1/integrity/audit` | re-verify the chain; return entries |
| GET | `/v1/aggregate` | k-anonymity-suppressed aggregates |
| GET | `/v1/clusters` | clustered queue view |

Every response is tested to contain no verdict language
(`test_no_api_response_uses_verdict_language`).

## 5. The deterministic rule engine

Seven rules in two tiers. Tier is part of the contract, not a label of convenience.

**Structural tier** — arithmetic contradictions that cannot both be true on a correct sheet:

| Rule | Detects |
|---|---|
| `R1_accredited_exceeds_registered` | accredited > registered |
| `R2_sum_mismatch` | valid votes + rejected ≠ accredited |
| `R5_duplicated_from_previous_unit` | every tally identical to the previous unit |

**Advisory tier** — statistical hints, labelled as such, never given structural weight:

| Rule | Detects |
|---|---|
| `R3_digit_transposition` | adjacent-digit swap between two tallies |
| `R4_suspicious_round_numbers` | ≥3 tallies that are exact multiples of 50 |
| `R6_turnout_outlier` | robust median/MAD outlier against the cohort |
| `R7_negative_or_impossible` | negative or otherwise impossible values |

Design notes:

- **R6 uses median/MAD, not mean/σ.** A mean/σ test is itself dragged by the outliers it is meant
  to find. Median/MAD is resistant, and the rule abstains when the cohort is degenerate
  (zero spread) rather than dividing by zero.
- **Every finding carries innocent explanations.** A finding is not just "accredited > registered";
  it is that plus the three plausible transcription errors a reviewer should rule out first.
- **Every finding is machine-re-checkable.** The arithmetic certificate shows the figures and the
  imbalance so a human can confirm it with a pen.

## 6. The assistive layer

| Component | Model | Authority | Abstention |
|---|---|---|---|
| Severity assist | multinomial logistic regression over transparent lexical features | orders a queue only | yes — confidence below 0.55, untrained, or too little training data |
| Claim matcher | char n-gram TF-IDF (3–5) + cosine | returns a shortlist with prior labels | yes — below a similarity floor, or empty archive |
| Clustering | token/character Jaccard + category gate | groups for display | n/a (deterministic) |

The severity model is trained **on the fly** from the loaded synthetic incidents (a 75/25
deterministic split), so no model artefact or credential is required to run the prototype.

## 7. Frontend architecture

- **React + Vite**, no UI framework dependency; the design system is hand-built from tokens.
- **Six pages**, each answering one question, rather than one dashboard answering none:
  - *File a report* — capture, with on-device hashing and a receipt
  - *Reviewer queue* — harm-ranked items with per-item reasoning and a required decision
  - *Result checks* — deterministic findings, two tiers, arithmetic certificates
  - *Claim matching* — shortlist against the archive, with prior labels
  - *Integrity* — live re-verification of the chain, aggregates with a privacy floor
  - *About and limits* — what it does, what it refuses to do, conditions before real use
- **Offline:** a service worker caches the app shell only. It **never** caches `/v1/*`, so a
  reviewer can never see a stale result presented as live.
- **Accessibility:** WCAG 2.2 AA verified by axe-core (0 violations), semantic HTML, visible focus
  rings, 44 px touch targets, no meaning encoded in colour alone.
- **Responsive:** verified with no horizontal overflow at 1440, 834, 390 and 320 px.

## 8. Configuration and startup

`config.py` validates required settings at startup and fails fast rather than falling back to an
insecure default. The prototype needs **no credential of any kind** to run.

## 9. Deliberate non-choices

| Not built | Why |
|---|---|
| Result declaration / winner projection | Out of scope by ethics and by the official brief; would make the tool unsafe |
| Live INEC system access | Forbidden by the mission rules; the tool is offline and synthetic-data only |
| Reporter accounts | Accounts mean identity, which endangers sensitive reporters |
| A generic election chatbot | Saturated; and an unaccountable model must not answer electoral questions |
| LLM-generated explanations | A language model must not author a sentence about someone's evidence |
| Paid APIs / cloud services | Must run free and locally; no credential required |

## 10. Performance

The rule engine is pure integer arithmetic over in-memory records with no I/O and no inference on
the hot path: **~9 000–9 600 records/second** measured over 900 records (0.094 s). The assistive model is
consulted only when a reporter has not stated a severity.

## 11. Verification plan (how each claim is proven)

| Claim | Evidence |
|---|---|
| The engine catches anomalies | `evaluation/RESULTS.md` — recall 97.6 % on organisers' labels |
| Findings are true | 63/63 structural substantiation; certificate re-checkable by hand |
| Tampering is caught | 3 direct-DB tamper tests in `test_provenance.py` |
| Identity is not stored | `test_no_reporter_identity_is_stored` |
| No response asserts a verdict | `test_no_api_response_uses_verdict_language` |
| The UI is accessible | axe-core 0 violations, 6 pages × 2 viewports |
| The UI is responsive | 0 overflow, 6 pages × 4 viewports |
| The end-to-end journey works | Real-browser run: file → hash → queue → integrity |
| Quality cannot silently regress | `test_evaluation_guards.py` (8 locked contracts) |
