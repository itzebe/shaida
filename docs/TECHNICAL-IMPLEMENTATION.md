# Technical implementation

A short guide for a reviewer who wants to understand the code, run it, and check the claims.

## 1. Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.11+, FastAPI, Uvicorn | typed validation at the boundary; small surface |
| Store | SQLite (single file) | zero-dependency, inspectable, runs anywhere |
| Assistive ML | scikit-learn (`LogisticRegression`, `TfidfVectorizer`) | small, offline, no model download, no credential |
| Frontend | React 18 + Vite | no UI framework dependency; fast static build |
| Offline | service worker (hand-written) | caches the app shell only, **never** API responses |
| Tests | pytest (backend), axe-core + Playwright (frontend checks) | standard, free |

**No paid dependency, no API key, no cloud service.** The prototype runs entirely on a laptop.

## 2. Running it

```bash
# Backend
cd backend
python -m venv ../.venv && source ../.venv/bin/activate
pip install -r requirements.txt
python -m shdaida                       # http://127.0.0.1:8000

# Load data (in another shell)
curl -X POST http://127.0.0.1:8000/v1/results/load-official
python ../scripts/seed_demo.py http://127.0.0.1:8000

# Frontend
cd ../frontend && npm install && npm run dev   # http://127.0.0.1:5173
```

## 3. Where the important code lives

| Concern | File | What to look for |
|---|---|---|
| Deterministic rules | `backend/shdaida/rules.py` | `ALL_RULES`, tier assignment, `certificate()` |
| Tamper-evidence | `backend/shdaida/provenance.py`, `storage.py` | `chain_hash`, `verify_chain`, `audit_chain` |
| Triage weights | `backend/shdaida/assist.py` | `HARM_WEIGHTS`, `harm_priority` |
| Assistive model | `backend/shdaida/assist.py` | `SeverityAssist`, `ClaimMatcher`, abstention thresholds |
| Clustering | `backend/shdaida/cluster.py` | `Clusterer` |
| Verdict guard | `backend/shdaida/taxonomy.py` | `assert_no_verdict_language` |
| Privacy floor | `backend/shdaida/service.py` | aggregate suppression |
| HTTP surface | `backend/shdaida/api.py` | 18 endpoints, validation, rate limiting |
| Multilingual text | `backend/shdaida/text.py` | `normalise`, `tokenise`, `jaccard` |

## 4. The three invariants worth reading first

### 4.1 Tamper-evidence is verified by re-computation

```python
chain_hash = sha256(prev_chain_hash ‖ sha256(canonical_bytes(payload)) ‖ seq)
```

`storage.audit_chain()` **re-hashes the stored payload** rather than trusting the stored digest. If
a row is edited directly in SQLite, verification fails and names the row. Proven by
`test_audit_chain_detects_direct_database_tampering` and `test_audit_chain_detects_row_deletion`.

An earlier version trusted the stored digest. That was a genuine hole — editing payload and digest
together would have passed — and the fix is why the current code re-hashes.

### 4.2 There is no automated decision path

The only endpoint that resolves a report is `POST /v1/reports/{id}/review`, and it requires both a
decision and a reason. Everything else emits findings, scores or shortlists.

### 4.3 A model may not author a sentence about evidence

Reviewer explanations are template-filled from deterministic findings. The verdict-language guard
raises if forbidden vocabulary appears. Both are tested.

## 5. Test suite

```bash
cd backend && python -m pytest tests -q     # 111 passed, 2 warnings
```

| Module | Tests | Protects |
|---|---|---|
| `test_rules.py` | 25 | the deterministic engine and its boundaries |
| `test_provenance.py` | 13 | tamper-evidence, including direct-DB tampering |
| `test_api.py` | 22 | validation, error hygiene, privacy, no-verdict language |
| `test_assist.py` | 23 | abstention, transparent ranking, explanations |
| `test_evaluation_guards.py` | 8 | measured quality cannot silently regress |
| `test_text.py` | 14 | multilingual normalisation |

The two warnings are Starlette/httpx deprecation notices, not failures. See
[`../evaluation/TEST-CASES.md`](../evaluation/TEST-CASES.md) for every test and what it protects.

## 6. Evaluation

```bash
python evaluation/evaluate.py    # rewrites evaluation/results.json
```

Reproducible, deterministic, no seeds needed. The results and their honest interpretation are in
[`../evaluation/RESULTS.md`](../evaluation/RESULTS.md).

## 7. Frontend verification

Automated, against the production build:

| Check | Tool | Result |
|---|---|---|
| Accessibility (WCAG 2.0/2.1/2.2 A+AA) | axe-core, 6 pages × 2 viewports | 0 violations |
| Horizontal overflow | 6 pages × 4 viewports (1440/834/390/320) | 0 overflows |
| Runtime errors | console + page-error capture, 24 combinations | 0 errors |
| End-to-end journey | real browser: file → hash → queue → integrity | passed |

These checks found five defects the build and the backend suite could not see: one runtime crash
(an unpassed prop), three CSS overflows, and two accessibility failures. All fixed and re-verified.

## 8. Design decisions and their reasons

| Decision | Reason |
|---|---|
| Deterministic core is the source of truth | an unaccountable model output must never become an accusation |
| Small assistive models, trained locally | no credential, works offline, and being wrong is harmless |
| Template explanations, not generated | a language model must not author a sentence about someone's evidence |
| No identity field in the schema | the cleanest protection is to hold no identifying data |
| k-anonymity suppression, not rounding | rounding leaks by subtraction |
| Two-tier findings | statistical hints must never carry the weight of an arithmetic contradiction |
| median/MAD for the turnout outlier | a mean/σ test is dragged by the outliers it is looking for |
| Service worker never caches `/v1/*` | a stale cached "verified" result would be worse than no result |
| SQLite, single process | a prototype must be inspectable and runnable with no infrastructure |

## 9. Known limitations of the implementation

- Single-instance store; no high availability, no tenancy, no operator authentication (a real
  deployment must add these).
- The assistive model is untested on non-English incident text.
- No human-factors study of reviewer agreement.
- No load testing at scale.
- The verdict-language guard is a denylist: strong, but not a proof of the absence of all
  judgemental phrasing.

All are repeated in [`SAFETY-AND-LIMITATIONS.md`](SAFETY-AND-LIMITATIONS.md) and
[`EVALUATION-REPORT.md`](EVALUATION-REPORT.md) §10.
