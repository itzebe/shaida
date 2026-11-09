# Competition application — SHAIDA

Application-ready answers for the Rise Networks **#AI4Elections Hackathon 2026** application form
(<https://ai4elections.risenetworks.org/application>).

> **Two things to note before submitting.**
> 1. Answers are in English, as the official rules require.
> 2. **Personal applicant details are deliberately left blank** and marked `[TO BE COMPLETED BY
>    APPLICANT]`. The applicant submits the form personally.
>
> Every technical claim below is backed by a reproducible test in this repository. Nothing here is
> invented: there are no fabricated team members, partnerships, endorsements, user numbers, pilot
> results or performance figures.

---

## Project title

**SHAIDA — verifiable electoral evidence and human triage**

## One-line description

SHAIDA lets a citizen, observer or fact-checker lock in what they captured, test it against
objective public rules, and get it to a human reviewer with a reason — without the tool ever
declaring a result, accusing a person, or exposing the reporter.

## Track selection

**Primary: Track 5 — Election Observation and Citizen Accountability.**
Secondary: Track 2 (Electoral Data Intelligence), Track 4 (Electoral Cybersecurity and Resilience),
Track 3 (Inclusive and Multilingual Civic Tech).

## Team

`[TO BE COMPLETED BY APPLICANT — minimum 2, maximum 4 members; every member must register
individually and be identified as part of this team before the registration deadline]`

| Role | Name | Background | Registration confirmed |
|---|---|---|---|
| Team lead | `[TO BE COMPLETED]` | `[TO BE COMPLETED]` | `[ ]` |
| Member 2 | `[TO BE COMPLETED]` | `[TO BE COMPLETED]` | `[ ]` |
| Member 3 (optional) | `[TO BE COMPLETED]` | `[TO BE COMPLETED]` | `[ ]` |
| Member 4 (optional) | `[TO BE COMPLETED]` | `[TO BE COMPLETED]` | `[ ]` |

Pathway: `[TO BE COMPLETED — individual / academic / start-up]`
Contact email: `[TO BE COMPLETED]` · Phone: `[TO BE COMPLETED]`
Team members are of Nigerian origin and aged 18 or over: `[TO CONFIRM]`

---

## Problem statement

Nigerian electoral evidence is abundant and untrustworthy, and the arithmetic that anyone could
check by hand is rarely checked.

A citizen photographs a result sheet; within hours the image is re-compressed and re-posted, and by
the time anyone wants to act on it there is no way to prove *this* file is what was captured at
*that* time. An EC8A sheet carries its own internal arithmetic — register, accredited, rejected,
per-party tallies — and when those numbers do not close that is a deterministic contradiction,
computable in microseconds and rarely computed systematically before allegations are made. And a
CSO hotline receives thousands of messages on election day, mostly duplicates and noise, with a
handful describing intimidation or violence that need attention within the hour — while the
reporting tools collect names and precise GPS coordinates by default, which is exactly the data
that endangers the person reporting intimidation.

The gap is not more data or another model. It is **provenance, deterministic verification, privacy
and accountable human review in one workflow.**

## Proposed solution

SHAIDA is a working prototype with three capabilities:

1. **Verifiable capture.** A report is filed offline with **no identity of any kind** — there is no
   field for a name, phone or account. Evidence is SHA-256 hashed **on the device** before upload,
   and the report is linked into an append-only, hash-chained audit log. The reporter receives a
   reference and a hash they can use to prove the record was not altered.

2. **Deterministic procedural verification.** Result records are checked against objective public
   rules in two deliberate tiers: **structural** findings are arithmetic contradictions (accredited
   exceeds registered; valid votes plus rejected do not equal accredited; tallies duplicated from
   the previous unit), and **advisory** findings are statistical hints (digit patterns, round
   numbers, turnout outliers). Every finding ships with an arithmetic certificate anyone can
   re-check, and with the **plausible innocent explanations** a reviewer should rule out first.

3. **Privacy-preserving human triage.** Reports are ordered by harm using a **published weighted
   score** with every contribution itemised; duplicates are grouped; sensitive categories change
   handling, never the verdict. A reviewer must record a decision **and a reason**, written into the
   same tamper-evident log.

## How AI is used — and where it is not

This is the design decision that defines the project:

> **The deterministic layer is the source of truth. A model may only order, shortlist or suggest —
> never conclude. There is no automated decision path in the system.**

The AI is deliberately small, offline, and placed where being wrong is harmless:

- a **multinomial logistic regression** that suggests a severity **to order a queue** — it cannot
  create or change a finding;
- a **character n-gram TF-IDF retriever** that returns a **shortlist** of similar archived claims
  with their **prior human labels** — it has no truth model and labels nothing.

Both **abstain** rather than guess, and abstention is tested. Reviewer explanations are
**template-filled from deterministic findings**, never generated by a language model, so no
sentence about someone's evidence can be invented. Verdict vocabulary is blocked at runtime by a
guard that raises an exception if it appears.

## Data used

Only the **organisers' official synthetic starter pack** and synthetic data generated by this
project. **No live electoral system is accessed, scanned or tested at any point. No personal data
and no scraped content is used anywhere.** See [`DATASHEET.md`](../evaluation/DATASHEET.md) and
[`DATASET-METHODOLOGY.md`](../evaluation/DATASET-METHODOLOGY.md).

## Evidence of performance

Evaluated against the organisers' own held-out labels (900 synthetic result records, 42 labelled
anomalies), reproducible with one command:

| Measure | Result |
|---|---|
| Labelled anomalies detected (recall) | **97.6 %** |
| Records flagged | **5.4 %** |
| Clean records wrongly flagged | **0.8 %** |
| Structural findings genuinely true | **100 %** (63/63) |
| Claim matcher top-3 | 86.7 % |
| Triage lift, most serious decile | **+2.08** |
| Backend tests | **111 passed** |
| Accessibility (axe-core, WCAG 2.2 AA) | **0 violations** |
| Responsive overflow (1440/834/390/320 px) | **0** |

Weaknesses are reported, not hidden: the adjacent-digit rule scores precision 0.000 on this pack
because the pack's case is a different typo signature; the severity assist reaches 0.40 exact
accuracy against a 0.25 baseline. A tempting broad digit heuristic was measured at **49 % over-fire
and rejected**, and is kept permanently measured so it cannot return.

## Innovation and differentiation

The competition briefs warn against six saturated ideas — a chatbot, a misinformation classifier, a
result dashboard, a polling-unit reporting app, an EC8A OCR tool, and a generic incident form.
SHAIDA is none of them. We assessed **16 prior artefacts**, and no operational product combines
offline verifiable capture, cryptographic evidence hygiene, deterministic procedural verification,
privacy-by-default handling, harm-ranked multilingual triage, and accountable human adjudication in
one Nigerian-context workflow.

See [`INNOVATION-AND-DIFFERENTIATION.md`](INNOVATION-AND-DIFFERENTIATION.md) and
[`research/02-competitor-landscape.md`](../research/02-competitor-landscape.md).

## Responsible AI and data protection

- **Nonpartisan by construction:** no candidate or party entity exists in the schema, and there is
  no channel through which the system could reach a voter, so microtargeting is architecturally
  impossible.
- **Privacy by architecture:** identity is not minimised, it is **absent**; location is off by
  default and coarsened; aggregates are suppressed below a k-anonymity floor, never rounded.
- **Human oversight mandatory:** no automated decision path exists; every review requires a
  decision and a reason.
- **NDPA 2023:** design-aligned; a formal DPIA is a **precondition for real use**, not a completed
  step.

See [`RESPONSIBLE-AI.md`](RESPONSIBLE-AI.md), [`DATA-PROTECTION.md`](DATA-PROTECTION.md) and
[`SAFETY-AND-LIMITATIONS.md`](SAFETY-AND-LIMITATIONS.md).

## Impact and scalability

The mechanism is built and verified: evidence stops degrading, deterministic contradictions are
surfaced before allegations, and attention is allocated by harm. The real-world outcome is
**unmeasured** — no human-factors study and no field pilot have been run, and we do not claim one.
Scalability is honest: the deterministic core scales naturally; the single-instance store and the
absence of tenancy are deliberate prototype simplifications, both named. See
[`IMPACT-AND-SCALABILITY.md`](IMPACT-AND-SCALABILITY.md).

## Deliverables in this repository

Working prototype (FastAPI backend + React frontend, runs with no API key or paid service), 111
backend tests, an evaluation harness with a documented methodology, official-template Model Card,
Safety and Limitations statement, Datasheet and Evaluation Report, research documents for all four
phases, a user guide, and a demo video.

## Declarations

- **No live or institutional electoral system has been accessed, scanned, probed or tested** at any
  point. All security work is defensive and is demonstrated against our own store in a unit test.
- **Only synthetic, public or organisers-provided data** is used. No personal data, no scraping.
- **This project is newly built for this competition** and has **not** received any prior grant,
  award or recognition in another competition.
- **Human oversight is mandatory**; the tool flags and does not judge.
- **Winning is not approval for operational deployment.**
- **AI assistance is disclosed** in [`README.md`](../README.md).

---

## Suggested short answers for form fields

**In one sentence, what does your solution do?**
It lets citizens, observers and fact-checkers capture electoral evidence with no identity, prove it
was not altered, check result-sheet arithmetic against objective rules, and route the riskiest
reports to a human reviewer — without the tool ever declaring a verdict.

**What makes it different from existing tools?**
It is built so that a model is never the source of truth: a deterministic engine computes and flags,
a small offline model only orders or shortlists and may abstain, and every decision requires a named
human and a reason written to a tamper-evident log.

**Which track?**
Track 5 primarily, with Track 2, Track 4 and Track 3.

**Is it a working prototype or an idea?**
A working prototype: a real FastAPI service and a real React frontend, 111 passing tests, an
evaluation harness, and a reproducible one-command run with no credential required.

**What are its limitations?**
It cannot tell you who won or whether fraud occurred, and it is designed not to. Its assistive model
is untested on non-English incident text; no human-factors study has been run; it has not been
load-tested at scale; and it needs an independent security review and a DPIA before any real use.

**Team and contact**
`[TO BE COMPLETED BY APPLICANT]`
