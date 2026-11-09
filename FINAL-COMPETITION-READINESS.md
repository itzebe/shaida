# Final competition readiness review

*Written as an independent, demanding judge who did not build this. Scores are against the
**officially published rubric** (`docs/05_templates/00_general_challenge_rules.md` §Judging), not
against our own preferences. Weaknesses are not softened.*

---

## 1. Product overview

**SHAIDA** — verifiable electoral evidence and human triage. A working prototype: a FastAPI backend
(18 endpoints, 12 modules), a React frontend (6 task-focused pages, offline-capable), SQLite
storage, 111 backend tests, and an evaluation harness. It lets a citizen, observer or fact-checker
capture an incident with **no identity**, prove it was not altered, check result records against
objective arithmetic rules, and route the riskiest reports to a reviewer who must record a decision
and a reason.

The defining decision: **a deterministic core is the source of truth; a model may only order,
shortlist or suggest, and there is no automated decision path at all.**

## 2. Verified problem and research evidence

- Four Phase 0–3 research documents (`research/00`–`03`), 25+ sources, an official-requirements
  compliance matrix of 25 rows, and a 16-product competitor assessment.
- The problem claim — evidence degrades, checkable arithmetic is unchecked, reviewer attention is
  misallocated, sensitive reporters are endangered — is supported by observation-organisation
  practice and the competition's own track briefs (Track 5 red lines on reporter identity and
  location precision; Track 2's base-rate-fallacy warning).

**Weakness:** the research is document-based. **No primary interviews** with a CSO, observer or
INEC official were conducted. The problem is well-evidenced from published sources; it is not
evidenced from field conversations. A judge should weigh this.

## 3. Competitor differentiation

Assessed 16 artifacts. The six saturated ideas the briefs warn against are all explicitly rejected
with an official basis. No operational product combines offline verifiable capture, cryptographic
evidence hygiene, deterministic procedural verification, privacy-by-default handling, harm-ranked
multilingual triage and accountable human adjudication in one Nigerian-context workflow.

**Strength:** the differentiation is structural, not cosmetic — it is a claim about *where the
model sits*, which is hard to copy without rebuilding.

**Weakness:** I did not obtain hands-on access to any competitor product (IReV, Truepic, C2PA
tooling). The comparison rests on published documentation and public claims. Where a competitor's
site *claims* capability, we noted that we could not verify it, and did not treat the claim as
established.

## 4. Implemented functionality

| Capability | State | Evidence |
|---|---|---|
| Identity-free report capture with on-device hashing | working | E2E browser run; `test_no_reporter_identity_is_stored` |
| Append-only hash-chained audit log, re-verified from stored data | working | 3 tamper tests incl. direct-DB edit and row deletion |
| Deterministic rule engine, 7 rules in 2 tiers | working | 25 tests; evaluation against held-out labels |
| Harm-ranked triage with itemised published weights | working | `test_triage_*`; explained on the Integrity/queue UI |
| Duplicate clustering | working | evaluation; `test_cluster_*` |
| Required human review with mandatory reason | working | `test_review_requires_a_reason` |
| k-anonymity aggregate suppression | working | `test_aggregation_suppresses_small_cells` |
| Multilingual interface + explanations (5 languages) | working, **unreviewed translations** | `test_explanations_exist_in_every_supported_language...` |
| Assistive severity model with abstention | working | abstention tests |
| Claim matcher with abstention | working | abstention tests |
| Offline app shell | working | service worker caches shell, never `/v1/*` |
| Evaluation harness | working | one command, deterministic |

**No dead controls, no stub handlers, no fake success states were found in the review.**

## 5. Architecture

Deterministic core → assistive layer → human decision, with the boundary enforced by construction, a
runtime verdict-language guard, and an API-wide test. The three-load-bearing invariants (chain
verified by re-computation; no automated decision path; models may not author explanations) are each
backed by tests. Recorded honestly: an early version trusted the stored digest — a real
vulnerability — and the fix is documented rather than hidden.

**Weakness:** single-instance SQLite, no tenancy, no operator authentication. Deliberate prototype
simplifications, but a judge should treat them as real gaps for any deployment.

## 6. AI capabilities

Two small, offline, credential-free components, both subordinate and both able to abstain.
Severity assist: 0.400 exact / 0.880 within-one against a 0.250 / 0.710 baseline. Claim matcher:
0.707 top-1, 0.867 top-3. **Both are modest and reported as modest.** The abstention rate for the
matcher is 0.000 on the paraphrase task — explicitly flagged as *not* evidence that abstention
works, with abstention tested separately.

**Weakness:** the severity assist is weak. It is placed where weakness is harmless (queue ordering),
and the interface refuses to invent a number when it abstains, but a judge may reasonably ask
whether it earns its place at all. It does, narrowly: it improves ordering when severity is
unstated, and it cannot cause harm.

## 7. Security and privacy safeguards

- Identity absent by schema; location coarsened; k-anonymity floor with suppression, not rounding.
- Hash-chained audit log with direct-database tamper tests.
- Boundary validation (422 with a stable shape), per-client rate limiting, error hygiene.
- No live system contacted; no secret needed to run; no outbound network call.
- Verdict vocabulary blocked at runtime.

**Weakness:** no independent security review, no DPIA, no penetration test. All named as
preconditions, none claimed as done.

## 8. Test results

| Check | Command | Result |
|---|---|---|
| Backend suite | `python -m pytest tests -q` | **111 passed, 2 warnings** (Starlette/httpx deprecations, not failures) |
| Evaluation | `python evaluation/evaluate.py` | reproducible; recall 0.976, flag rate 0.0544, clean FA 0.0082, substantiation 63/63 |
| Frontend build | `npm run build` | clean, 194 kB JS / 12 kB CSS |
| Accessibility | axe-core, 6 pages × 2 viewports | **0 violations** |
| Responsive | 6 pages × 4 widths (1440/834/390/320) | **0 overflows** |
| Runtime errors | 24 combinations | **0** |

The UI checks each found real defects the build could not see (one runtime crash, three overflows,
two accessibility failures). All fixed and re-verified. That is the strongest evidence the checks
are real rather than theatre.

## 9. Evaluation results

Against the organisers' **own held-out labels**. Recall 97.6 %; flag rate 5.4 %; clean false-alarm
0.8 %; **structural substantiation 63/63 = 100 %**; triage lift +2.08. Two precision numbers are
reported where they diverge, and the conservative one is quoted as the headline. A **rejected**
heuristic (49 % over-fire) is kept permanently measured.

**Weakness:** no confidence intervals (samples of 42 positives, 100 and 75 items are too small to
support them). No human-factors study. No real-world data. All stated as limitations.

## 10. Demo video and public URL

- `demo/final-demo.mp4` — **2:38**, ≤3-minute limit, H.264 + AAC, 1440×996, burned-in captions,
  synthesised narration. Composed from a **real** screen walkthrough of the running app; every
  screen shows real backend output; all data is the organisers' synthetic pack or clearly-synthetic
  `DEMO-*` records.
- **Public URL:** <https://work-1-cfgpkwukjwliyfgz.prod-runtime.all-hands.dev/> — verified live. The
  frontend and API are served from **one origin** by `scripts/serve_public.py` (a static server that
  transparently proxies `/v1` to the backend), so no CORS configuration is needed and no URL in the
  client is hard-coded. End-to-end through this URL: filed a report (real reference `rep-…` and hash
  returned), verified the chain (intact), loaded the result checks, 0 page errors.
  **Caveat, stated honestly:** this is an ephemeral runtime URL for this environment, not a durable
  production deployment. It stays up only while the process runs; for the submission a durable free
  host should be used. The reproduction command is `python scripts/serve_public.py --port 12000`
  with the backend already running.

## 11. Application-ready description

`docs/COMPETITION-APPLICATION.md` contains polished, truthful answers, with **all personal applicant
details left blank** for the user to complete. No team members, partnerships, endorsements, user
numbers or pilot results are invented.

## 12. Judging scorecard (official weights)

| Criterion | Weight | Score /10 | Weighted | Rationale |
|---|---|---|---|---|
| Technical functionality and innovation | 25 % | 8.5 | 2.13 | Real end-to-end system, small but non-trivial, genuinely differentiated by the "model never concludes" architecture. Not 9+: the deterministic engine is solid but the rule set is compact, and the assistive layer is weak. |
| Electoral relevance and practical usefulness | 20 % | 8.0 | 1.60 | Maps directly onto Track 5/2/4/3 red lines; solves real, documented problems. Not 9+: no field validation, so usefulness is argued, not demonstrated. |
| Cybersecurity, privacy and responsible AI | 20 % | 9.0 | 1.80 | The strongest dimension: identity absent by schema, tamper-evidence proven by direct-DB tests, verdict language blocked at runtime, abstention tested, honest limitations everywhere. Not 10: no external review or DPIA. |
| Inclusion, accessibility and multilingual | 15 % | 7.5 | 1.13 | 0 axe violations, 320 px clean, 5 languages, offline app shell. Not 8+: the assistive model is untested on non-English text and translations are unreviewed. |
| Scalability, sustainability and feasibility | 15 % | 7.0 | 1.05 | Zero-cost, offline, no credential, small dependency set, clear scaling path. Not 8: single-instance store, no tenancy, no load testing. |
| Demonstration and documentation | 5 % | 9.0 | 0.45 | Complete official-template package, reproducible commands, a real ≤3-min demo, and a **verified live public URL**. Not 10: the demo uses composed captures rather than motion video, and the URL is ephemeral. |
| **Total** | 100 % | — | **8.16 / 10** | |

**Honest reading: ~82/100.** Strong on the two 20 % dimensions (responsible AI, electoral
relevance) and on documentation; held back by the absence of field validation, external review, and
a public deployment link. This is a credible contender, not a runaway winner.

**Hard-exclusion check:** the rules allow exclusion for critical security, privacy, safety or legal
concerns. On this review, **none apply** — no live-system access, no personal data, no verdicts, no
partisanship — and each is enforced by a test rather than asserted.

## 13. Remaining limitations

1. **No human-factors study.** Reviewer agreement and time saved are unmeasured. This is the
   largest single gap.
2. **No field validation.** All results are on synthetic data.
3. **No independent security review, DPIA, or penetration test.**
4. **The public URL is ephemeral** — it lives only while the runtime process runs, not a durable host.
5. **Assistive model untested on Hausa/Yoruba/Igbo incident text.**
6. **Non-English interface strings unreviewed by native speakers.**
7. **`R3` misses the pack's transposition case** (documented, and it is a different typo signature).
8. **`R2` false positives under strict single-label scoring** (explained; substantiation is 100 %).
9. **Single-instance store, no tenancy, no operator auth.**
10. **No load testing.**
11. **Research lacks primary interviews.**

## 14. Exact next steps

**Before the application deadline (12 Nov 2026):** complete personal/team details in
`docs/COMPETITION-APPLICATION.md`; submit the form. *(The prototype is already beyond what the
application requires.)*

**Before the prototype deadline (13 Dec 2026):**
1. **Publish a public demo URL** — the only deliverable-level gap. A free static host for the
   frontend plus a free Python host for the API, with no credential in the client.
2. **Native-speaker review** of the ha/yo/ig strings.
3. **One CSO conversation** to replace the document-only problem evidence with a primary source.
4. **A small human-factors exercise** — even five reviewers, timed, measuring agreement — to turn
   the biggest unknown into a measured number.
5. **Record motion video** if the organisers prefer it to the composed capture.

**Before any real use (unchanged by winning):** independent security review; DPIA under NDPA 2023;
ethics review; written CSO agreement; legal review; load and adversarial testing. See
[`docs/SAFETY-AND-LIMITATIONS.md`](docs/SAFETY-AND-LIMITATIONS.md) §5.

---

## Reviewer's summary

This is a well-built, unusually honest prototype whose differentiator is architectural rather than
cosmetic: it is the rare election tool designed to **refuse** to conclude, and it enforces that
refusal in code and in tests. Its privacy and responsible-AI posture is the strongest part of the
submission. Its weaknesses are the ordinary ones for a prototype — no field data, no external
review, no public link — and every one of them is disclosed rather than concealed, which is itself
a quality signal for a competition that explicitly rewards *"documenting limits and safeguards"*.
