# SHAIDA

**Verifiable electoral evidence and human triage.**
*Hausa: shaida — "testimony", "evidence".*

A working prototype built for the **Rise Networks #AI4Elections Hackathon 2026**.

SHAIDA lets a citizen, observer or fact-checker **lock in what they captured, test it against
objective public rules, and route it to a human reviewer with a reason** — without the tool ever
declaring a result, accusing a person, or exposing the reporter.

> **It flags. It does not judge.** Every automated output is a question addressed to a human, and
> the only way a report leaves the queue is a named human recording a decision *and a reason*.

---

## Why this is different

Most election-tech tools put a model where its output **is** the conclusion — a chatbot that
answers, a classifier that labels, a dashboard that implies. SHAIDA is built on the opposite
assumption:

> **The deterministic layer is the source of truth. A model is only ever allowed to order,
> shortlist or suggest — never to conclude.**

That single decision produces four properties that are hard to copy and easy to verify:

| Property | Evidence |
|---|---|
| **Verifiable provenance** | Evidence is SHA-256 hashed *on the device* before upload; the audit log is a hash chain re-computed from stored data. A test edits the database directly and proves tampering is caught. |
| **Deterministic checks that flag, never judge** | 7 rules in 2 tiers. Every structural finding's stated contradiction actually holds — **63/63 = 100 % substantiation**. Each ships an arithmetic certificate anyone can re-check with a pen. |
| **Privacy as architecture, not policy** | There is **no field** for a reporter's identity. Location is off by default and coarsened to ~1 km. Aggregates are suppressed below a k-anonymity floor, never rounded. |
| **Accountable human review** | No automated decision path exists. Every review requires a decision **and a reason**, written to the same tamper-evident chain. Every finding lists the innocent explanations to rule out first. |

---

## Measured results (against the organisers' own held-out labels)

| Measure | Result |
|---|---|
| Labelled anomalies detected (recall) | **97.6 %** (41/42) |
| Records flagged, of 900 | 49 (**5.4 %**) |
| Clean records wrongly flagged | **0.8 %** (7/858) |
| Structural findings genuinely true | **100 %** (63/63) |
| Claim matcher top-3 accuracy | 86.7 % |
| Triage lift for the most serious decile | **+2.08** |

Two numbers are reported as **weak, on purpose**, because hiding them would be dishonest:
`R3_digit_transposition` scores precision 0.000 on this pack (its target case is a different typo
signature — see [`evaluation/RESULTS.md`](evaluation/RESULTS.md) §2.2), and the severity assist
reaches only 0.40 exact accuracy against a 0.25 baseline. Both are explained rather than excused.

A tempting heuristic that flags two tallies differing in one digit was **measured at 49 % over-fire
and rejected** — kept permanently in the harness so it cannot return.

---

## Quick start

Requires Python 3.11+ and Node 18+. **No API key, no paid service, no credential of any kind.**

```bash
# 1. Backend  (terminal 1)
cd backend
python -m venv ../.venv && source ../.venv/bin/activate
pip install -r requirements.txt
python -m shdaida            # serves http://127.0.0.1:8000

# 2. Load the official synthetic pack and some demo reports
curl -X POST http://127.0.0.1:8000/v1/results/load-official
python ../scripts/seed_demo.py http://127.0.0.1:8000

# 3. Frontend  (terminal 2)
cd frontend
npm install
npm run dev                  # serves http://127.0.0.1:5173
```

Then open <http://127.0.0.1:5173>.

### Or run it as one origin (frontend + API behind a single URL)

```bash
cd frontend && npm run build && cd ..
python scripts/serve_public.py --port 12000   # with the backend already running
```

This serves the built frontend and transparently proxies `/v1` to the backend, so the whole app is
reachable at one URL with no CORS configuration. A live instance is verified at
<https://work-1-cfgpkwukjwliyfgz.prod-runtime.all-hands.dev/> while this runtime is up.

```bash
# Verify everything
cd backend && python -m pytest tests -q     # 111 tests
python evaluation/evaluate.py               # rewrites evaluation/results.json
```

---

## How it maps to the official tracks

| Track | What SHAIDA provides |
|---|---|
| **Track 5** — Observation and citizen accountability *(primary)* | Structured incident capture, evidence hygiene, harm-ranked triage, duplicate clustering |
| **Track 2** — Electoral data intelligence | Deterministic result-sheet checks with human review; anomaly surfacing, never fraud accusation |
| **Track 4** — Cybersecurity and resilience | Defensive: tamper-evident audit chain, privacy-preserving reporting, abuse-resistant API |
| **Track 3** — Inclusive and multilingual civic tech | Offline-capable app shell; interface and explanations in en, pcm, ha, yo, ig |
| **Track 1** — Information integrity | Near-duplicate claim shortlist against an archive with prior human labels (no truth model) |

---

## Repository map

```
backend/          FastAPI service — rules, provenance, triage, clustering, storage
  shdaida/        12 modules, 18 endpoints
  tests/          6 modules, 111 tests
frontend/         React + Vite, 6 task-focused pages, offline app shell
data/
  official-synthetic/   the organisers' starter pack (read-only)
evaluation/       harness, dataset methodology, results, test cases
research/         Phase 0–3: requirements, problem landscape, competitors, selection
docs/             product, architecture, security, AI, competition package
demo/             storyboard, narration, video
```

## Documentation

| Document | Contents |
|---|---|
| [`docs/PROJECT-ABSTRACT.md`](docs/PROJECT-ABSTRACT.md) | One-page abstract |
| [`docs/PROBLEM-STATEMENT.md`](docs/PROBLEM-STATEMENT.md) | Problem, users, evidence |
| [`docs/PRODUCT.md`](docs/PRODUCT.md) | Product definition, users, roadmap |
| [`docs/TECHNICAL-ARCHITECTURE.md`](docs/TECHNICAL-ARCHITECTURE.md) | Architecture and data model |
| [`docs/AI-METHODOLOGY.md`](docs/AI-METHODOLOGY.md) | Where a model may sit, and why |
| [`docs/MODEL-CARD.md`](docs/MODEL-CARD.md) | Official model/system card |
| [`docs/SAFETY-AND-LIMITATIONS.md`](docs/SAFETY-AND-LIMITATIONS.md) | Official safety statement |
| [`docs/SECURITY-AND-PRIVACY.md`](docs/SECURITY-AND-PRIVACY.md) | Threat model, NDPA alignment |
| [`docs/RESPONSIBLE-AI.md`](docs/RESPONSIBLE-AI.md) | Responsible-AI safeguards |
| [`docs/DATA-PROTECTION.md`](docs/DATA-PROTECTION.md) | Data protection and NDPA 2023 |
| [`docs/INNOVATION-AND-DIFFERENTIATION.md`](docs/INNOVATION-AND-DIFFERENTIATION.md) | Against 15+ prior systems |
| [`docs/IMPACT-AND-SCALABILITY.md`](docs/IMPACT-AND-SCALABILITY.md) | Impact and honest scaling path |
| [`docs/EVALUATION-REPORT.md`](docs/EVALUATION-REPORT.md) | Official evaluation report |
| [`docs/USER-GUIDE.md`](docs/USER-GUIDE.md) | How each user uses it |
| [`docs/COMPETITION-APPLICATION.md`](docs/COMPETITION-APPLICATION.md) | Application-ready answers |
| [`evaluation/DATASHEET.md`](evaluation/DATASHEET.md) | Official datasheet |
| [`evaluation/RESULTS.md`](evaluation/RESULTS.md) | Full measured results |
| [`evaluation/TEST-CASES.md`](evaluation/TEST-CASES.md) | Every test, and what it protects |
| [`research/`](research/) | Requirements, problem landscape, competitor analysis, selection |
| [`FINAL-COMPETITION-READINESS.md`](FINAL-COMPETITION-READINESS.md) | Independent readiness assessment |

---

## Licence

Code: **MIT**. Documentation and synthetic data: **CC BY 4.0**. See [`LICENSE`](LICENSE).

## AI assistance disclosure

This prototype and its documentation were produced with the assistance of an AI coding agent
(OpenHands), working under the direction of the applicant. All technical decisions, all code, and
all reported results were produced and verified within this repository; the verification commands
are given above and in every results document, so every claim can be re-checked independently.
This disclosure is provided as required by the competition's contributing guidelines.

## Declarations

- **No live electoral system has been accessed, scanned, probed or tested at any point.** All data
  is the organisers' synthetic pack or synthetic data generated by this project.
- **The project is newly built for this competition** and has not received any prior grant, award
  or recognition.
- **Winning is not approval for deployment.** See
  [`docs/SAFETY-AND-LIMITATIONS.md`](docs/SAFETY-AND-LIMITATIONS.md) §6.
