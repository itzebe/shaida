# Project abstract

**Project:** SHAIDA — verifiable electoral evidence and human triage
**Track:** Track 5 (Observation and citizen accountability), with Track 2, Track 4 and Track 3
**Competition:** Rise Networks #AI4Elections Hackathon 2026
**Status:** Working prototype, v1.0.0

---

## The problem in one paragraph

Nigerian electoral evidence is abundant and untrustworthy. A photo of a result sheet, a voice note
about intimidation, a claim spreading on WhatsApp — all of it circulates, and none of it can be
proven later to be what it was when it was captured. At the same time, the arithmetic that
*anyone* could check by hand on an EC8A sheet is rarely computed systematically, and the few
organisations able to check it are drowning: a CSO hotline receives thousands of messages, mostly
duplicates and noise, with a handful that need attention urgently. Meanwhile the reporting tools
collect names, phone numbers and GPS coordinates by default — exactly the data that endangers a
person who reports intimidation or violence.

## The product

**SHAIDA** (Hausa: *testimony*, *evidence*) is a privacy-preserving electoral evidence and triage
system. A citizen, observer or fact-checker can:

1. **Capture** an incident on a low-end phone, **offline**, with a photo or scan hashed **on the
   device** before upload, and **without giving any identity** — no name, no phone, no account.
2. **Test** result-sheet records against objective, public rules: whether the sheet's own numbers
   close, whether accreditation exceeds the register, whether tallies duplicate the previous unit.
3. **Route** the report to a human reviewer through a harm-ranked queue, with duplicates grouped and
   every item showing *why* it ranks where it does and which innocent explanations to rule out
   first.

A reviewer must record a decision **and a reason**, which is written to a tamper-evident audit log
anyone can re-verify.

## The one design decision that defines it

Most election-tech tools put a model where its output **is** the conclusion. SHAIDA inverts that:

> **The deterministic layer is the source of truth. A model may only order, shortlist or suggest —
> never conclude. And there is no automated decision path at all.**

The AI is therefore small, optional, and placed where a wrong answer is harmless: a severity model
that orders a queue, and a retriever that shortlists similar archived claims. Both abstain rather
than guess. Reviewer explanations are template-filled from deterministic findings, so a language
model can never author a sentence about someone's evidence. Verdict vocabulary is blocked at
runtime by a guard that raises an exception if it appears.

## Measured results

Evaluated against the organisers' own held-out labels (900 synthetic records, 42 labelled):

| Measure | Result |
|---|---|
| Labelled anomalies detected | **97.6 %** |
| Records flagged | **5.4 %** |
| Clean records wrongly flagged | **0.8 %** |
| Structural findings genuinely true | **100 %** (63/63) |
| Claim matcher top-3 | 86.7 % |
| Triage lift for the most serious decile | **+2.08** |
| Accessibility (axe-core, WCAG 2.2 AA) | **0 violations** |

Weaknesses are reported, not hidden: the adjacent-digit rule scores precision 0.000 on this pack
because the pack's case is a different typo signature, and the severity assist reaches 0.40 exact
accuracy against a 0.25 baseline. A tempting broad digit heuristic was measured at **49 % over-fire
and rejected**, and is kept permanently measured so it cannot return.

## Why it can win

It is not another chatbot, classifier, dashboard, reporting form or OCR tool — all of which the
competition briefs warn against. It is the one artefact that combines **evidence provenance**,
**deterministic procedural verification**, **privacy-preserving triage**, and **accountable human
review** in a single Nigerian-context workflow, with every claim backed by a reproducible test.

It also respects the briefs' hardest constraint: it is a tool that **refuses to declare a verdict**,
and it enforces that refusal in code.
