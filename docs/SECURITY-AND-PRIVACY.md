# Security, privacy and responsible AI

This document states what SHAIDA protects, how, and what it explicitly does **not** claim. It is
written to survive an adversarial read by a security reviewer, not to reassure one.

---

## Part A — Security

### A1. Trust boundaries

```
  UNTRUSTED                    │  BOUNDARY            │  TRUSTED
  ─────────────────────────────┼──────────────────────┼───────────────────────
  browser input, evidence      │  Pydantic validation │  service layer,
  uploads, query strings,      │  at the API edge;    │  rules, storage
  claim text, coordinates      │  length + enum +     │
  ─────────────────────────────┼──────────────────────┼───────────────────────
  everything fetched from the  │  treated as data,    │  —
  network                      │  never as instruction│
```

Validation happens **once**, at the boundary. Inside the system, internal types are trusted —
there are no scattered defensive checks for conditions the schema already rules out.

### A2. Input validation and injection

- All request bodies are validated by Pydantic models. Invalid input returns **HTTP 422** with a
  stable shape (`test_invalid_input_is_rejected_with_422`).
- Narratives are length-bounded (`SHAIDA_MAX_REPORT_CHARS`, default 2000); over-length input is
  rejected rather than truncated (`test_narrative_over_the_limit_is_rejected`).
- Numeric result fields are bounded and reject negative values at the boundary
  (`test_result_batch_rejects_negative_tally_at_the_boundary`).
- **SQL:** every statement uses parameterised placeholders. There is no string-built SQL anywhere
  in `storage.py`.
- **No `eval`, no shell, no template injection.** Claim text is normalised and compared, never
  executed.
- **Error hygiene:** errors return a stable shape and never echo a stack trace, a path or an
  internal identifier (`test_error_shape_is_stable_and_leaks_nothing`).

### A3. Authentication and authorization

- The prototype has **no accounts**, by design — accounts imply identity, which endangers
  sensitive reporters. There is no authentication surface to attack.
- **Object-level authorization is therefore not applicable to a user-owned resource**, because no
  report is owned by an identifiable user. This is a deliberate trade-off and it is stated rather
  than glossed: when a real deployment introduces CSO-operated instances, it must add operator
  authentication and per-tenant scoping, and that is listed as a precondition for real use in
  `docs/PRODUCT.md` §14 and on the About page.

### A4. Abuse control

- Per-client write rate limiting (default 60/min) to blunt automated flooding
  (`test_rate_limiter_blocks_after_the_limit`, `test_rate_limiter_is_per_client`).
- Duplicate and near-duplicate reports cluster, so flooding the queue is not the same as flooding
  the reviewer's attention.

### A5. Data integrity — the tamper-evident chain

`chain_hash = SHA256(prev_chain_hash ‖ payload_hash ‖ seq)`

Properties, each proven by a test:

| Property | Test |
|---|---|
| Editing an entry breaks the chain | `test_chain_detects_an_edited_entry` |
| Deleting an entry breaks the chain | `test_chain_detects_a_deleted_entry` |
| Reordering entries breaks the chain | `test_chain_detects_reordering` |
| Renumbering is caught (seq is inside the hash) | `test_chain_hash_binds_sequence_number` |
| **A direct SQL edit of a stored row is caught** | `test_audit_chain_detects_direct_database_tampering` |
| **A direct SQL row deletion is caught** | `test_audit_chain_detects_row_deletion` |

The two direct-database tests are the ones that matter. They do not call the application to
tamper; they open the database and alter it behind the application's back.

> **Fixed vulnerability, recorded.** An earlier implementation trusted the stored `payload_hash`.
> That is a genuine hole: editing the payload *and* its stored digest together would verify
> cleanly. The fix was to re-hash the stored payload from scratch on every verification. This is
> recorded because a "tamper-evident" claim is exactly where this class of flaw hides.

### A6. Secrets

- The prototype requires **no credential of any kind** to run. There is no API key, no token, no
  database password.
- No secret is stored in the repository. Configuration is read from the environment with validated
  defaults, and `config.py` fails fast on an implausible value rather than falling back silently
  (`SHAIDA_MAX_REPORT_CHARS is implausibly small`).

### A7. Supply chain

- Backend dependencies: FastAPI, Uvicorn, Pydantic, pytest — all mainstream and pinned in
  `requirements.txt`.
- Frontend: React + Vite only. No UI framework, no charting library, no analytics.
- No dependency is added for a task the standard library can do.

### A8. What was deliberately *not* done (cybersecurity scope)

The mission forbids attacking, scanning or probing live electoral infrastructure. Accordingly:

- **No live INEC or other institutional system is contacted, scanned or tested at any point.**
- The cybersecurity dimension of the product is *defensive*: integrity, provenance, abuse
  resistance, and privacy.
- Where an offensive technique would have been illustrative (e.g. demonstrating a tamper), it is
  performed against **our own SQLite store**, in a unit test, on synthetic data.

---

## Part B — Privacy (NDPA 2023 aligned)

### B1. Data minimisation — by schema

| Data | Collected? | Note |
|---|---|---|
| Reporter name | **No** | no column exists |
| Phone / email / account | **No** | no column exists |
| IP address | **No** | not stored |
| Reporter *role* | Yes | citizen / observer / party agent / official — a role, not a person |
| Narrative | Yes | the substance of the report |
| Evidence file | Hashed | the hash is trusted; the blob is stored to allow re-verification |
| Precise location | **Off by default** | if used, coarsened to ~1 km and never returned exactly |
| Polling-unit code | Optional | a public identifier, not a person |

`test_no_reporter_identity_is_stored` creates a report and asserts that no identity field exists
in the stored record. `test_coordinates_are_coarsened_and_never_returned_exactly` asserts location
handling.

### B2. Purpose limitation

Report data is used to route the report to a human reviewer and for nothing else. There is no
profiling, no advertising, no microtargeting, and no partisan use. The mission rules forbid
partisan political persuasion and voter microtargeting; the architecture makes them impossible
because the tool has no channel to reach a voter at all.

### B3. Storage limitation and honest scope

The store is a **prototype** SQLite file, documented as such. No production retention or
deletion policy is claimed, because claiming one without a live deployment would be dishonest.
A retention policy is listed as a precondition for real use.

### B4. Aggregation with a privacy floor

Aggregates are published only with a **k-anonymity floor** (default k = 5). Cells below the floor
are **suppressed entirely, never rounded**, so an individual report cannot be recovered by
subtraction (`test_aggregation_suppresses_small_cells`). The Integrity page shows the suppression
count and the floor openly.

### B5. Protecting vulnerable reporters

- Sensitive categories (`intimidation`, `voter_intimidation`, `violence_or_threat`) change
  **handling**: identity is stripped, location is coarsened further, and a reviewer is notified.
  They never change the verdict — being a victim of intimidation is not evidence of wrongdoing.
- The interface tells a reporter, in plain language, to consider leaving location blank for such
  reports.
- SHAIDA never contacts the police, INEC or any authority on its own. It says so on the receipt.

### B6. Honest limits

No DPIA has been performed; none is claimed. The About page lists a formal NDPA 2023
data-protection review as a **precondition** for real use, not as completed work.

---

## Part C — Responsible AI

### C1. The single governing rule

> **SHAIDA never makes an electoral decision.** Its outputs are questions addressed to a human.

This is enforced in three places, not merely asserted:

1. **By construction** — the rule engine produces findings with a tier and a message; the triage
   layer produces a score with a breakdown; neither produces a conclusion.
2. **By a runtime guard** — `taxonomy.assert_no_verdict_language()` raises `VerdictLanguageError`
   if any generated text contains forbidden verdict vocabulary (e.g. "fraudulent", "corrupt",
   "falsified"). It is called on generated explanations and asserted in
   `test_no_finding_uses_verdict_language` and
   `test_explanations_exist_in_every_supported_language_and_avoid_verdicts`.
3. **By an API-wide test** — `test_no_api_response_uses_verdict_language` walks responses and
   asserts none asserts a verdict.

### C2. AI is never the source of truth

| Component | What it may do | What it may never do |
|---|---|---|
| Severity assist | suggest a severity to order a queue | create a finding or change one |
| Claim matcher | return a shortlist with prior reviewer labels | label a claim true/false |
| Clustering | group similar reports for display | merge evidence into a new claim |

Both assistive components **abstain** rather than guess, and abstention is tested:
`test_matcher_abstains_on_unrelated_text`,
`test_matcher_abstains_when_below_the_floor_even_with_a_weak_match`,
`test_severity_assist_abstains_when_the_posterior_is_flat`,
`test_severity_assist_abstains_when_untrained`,
`test_severity_assist_abstains_when_training_data_is_too_small`.

### C3. No fabricated content, no fabricated explanations

Explanations are **template-filled from deterministic findings**, not written by a language model.
This is why a sentence about someone's evidence can never be invented. The About page states this
in the same words.

### C4. Uncertainty is shown, not hidden

- Advisory findings are labelled advisory in the UI and never carry structural weight.
- Every finding lists the **plausible innocent explanations** a reviewer should rule out first —
  transcription error, misread faint form, merged rows.
- The severity assist reports its training size and its abstention behaviour.
- The About page states plainly that Hausa, Yoruba and Igbo strings are **first-pass translations
  that have not yet been reviewed by native speakers**.

### C5. Human oversight is mandatory

- The only way a report leaves the queue is `POST /v1/reports/{id}/review`, which **requires** a
  decision and a reason (`test_review_requires_a_reason`).
- The decision and its reason are written into the same hash-chained audit log
  (`test_review_is_recorded_and_audited`).
- The API rejects an unknown decision value (`test_review_rejects_unknown_decision`).

### C6. Honesty about scope and maturity

The footer of every page states: *"SHAIDA is a working prototype built for the Rise Networks
#AI4Elections Hackathon 2026. It is not approved for operational deployment and does not access any
live electoral system."* The About page lists six conditions that must be met before any real use,
and states that winning the competition would not skip them.

---

## Part D — Residual risks (stated, not hidden)

| Risk | Severity | Status |
|---|---|---|
| No independent security review yet | High | Listed as a precondition for real use |
| Non-English strings unreviewed by native speakers | Medium | Stated on the About page |
| No DPIA yet | High | Listed as a precondition |
| `R3` produces false positives on this pack | Medium | Documented in `evaluation/RESULTS.md` §2.2; advisory tier only |
| Single-instance SQLite store; no HA | Medium | Acceptable for a prototype; a pilot needs a real store |
| No human-factors study of reviewer agreement | Medium | Not measured; stated as a limitation |
| Untested at national scale / under load | High | Stated in `evaluation/RESULTS.md` §6 |
| Location coarsening is a privacy measure, not a formal guarantee | Low | Documented behaviour, tested |
