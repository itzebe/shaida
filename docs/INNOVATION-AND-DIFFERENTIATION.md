# Innovation and differentiation

## 1. The landscape

We assessed **16 prior artefacts** — Nigerian and international, operational and aspirational —
against the official briefs. The full assessment, with per-product weaknesses, is in
[`research/02-competitor-landscape.md`](../research/02-competitor-landscape.md). The short version:

| Class | Representative | Why it is not this |
|---|---|---|
| Institutional result portal | INEC IReV | Not collation; no citizen-side verifiable record |
| Observation coalition | Nigeria Civil Society Situation Room | Free-text, human-mediated; no integrity primitive |
| Parallel vote tabulation | YIAGA Africa | Sample-level, heavy; not unit-level triage |
| Fact-checking platform | FactCheckHub, Dubawa | Editorial and capacity-bound; after-the-fact |
| Narrative intelligence | Logically | Paid, enterprise, not Nigeria-grounded, not free |
| Deepfake detection | Reality Defender | Binary verdict, brittle, paid — the opposite of our approach |
| Capture provenance | Truepic | Commercial, non-electoral |
| Media provenance | Numbers Protocol | On-chain; public-ledger privacy risk |
| Provenance standard | C2PA | A standard, not a citizen workflow |
| Automated fact-checking | Full Fact | English/UK-centric |
| Community reporting | Tracka | Not electoral |
| Observation tooling | NDI/IRI/IFES | Mission-scoped, not a free offline PWA |
| Generic chatbot | many | Invents rules; no engineering |
| Generic classifier | many | Verdicts on speech; brittle |
| Result dashboard / PU app / EC8A OCR | many | Shows data; changes nothing |

## 2. The saturated ideas, explicitly rejected

The mission brief asked for particular scrutiny of six. Our verdicts, against official evidence:

| Saturated idea | Verdict | Official basis for rejection |
|---|---|---|
| Another generic election chatbot | **Reject** | Track 3 red line: "No invented electoral rules or dates"; the zero-unsupported-answers target makes an ungrounded chatbot a liability |
| Another ordinary misinformation classifier | **Reject** | Track 1: "No tool that auto-removes or publicly labels individuals' speech as false without human review" |
| Another election result dashboard | **Reject** | Track 2: "must not independently declare results" |
| Another polling-unit reporting application | **Reject** | Duplicates IReV and inherits the collation confusion |
| Another basic EC8A OCR tool | **Reject** | A component, not a product; leaves arithmetic, consistency and human review unaddressed |
| Another generic incident-reporting form | **Reject** | Track 5 red lines demand privacy-by-default, evidence hygiene and triage — a plain form does none |

## 3. The defensible gap

Across all 16 assessed artefacts, **no operational product** combines, for the Nigerian electoral
context:

1. independent, **offline-capable** capture of electoral evidence on a low-end phone;
2. **cryptographic evidence hygiene** — a content hash plus a hash-chained, tamper-evident audit log
   — with C2PA-compatible thinking;
3. **deterministic procedural verification** against objective public rules, producing **flags,
   never verdicts**, with an arithmetic certificate any observer can re-check by hand;
4. **multilingual, paraphrase-robust matching and harm-ranked triage** to save scarce reviewer time;
5. **privacy by default** — no reporter identity field at all, coarse location, k-anonymised
   aggregation;
6. **explicit human adjudication** with a full, reproducible audit trail.

That combination is SHAIDA.

## 4. What specifically differentiates it

### 4.1 It refuses to declare — and enforces the refusal in code

Every competitor above either declares (a classifier's label, a detector's score) or does nothing
automatable. SHAIDA's contribution is a system whose **strongest capability is a refusal**: it
computes deterministic contradictions and then declines to interpret them. This is not a disclaimer
bolted on; it is enforced by `taxonomy.assert_no_verdict_language()`, which raises an exception if
generated text contains verdict vocabulary, asserted across all five languages and across the whole
API surface.

### 4.2 The AI is placed where being wrong is harmless

| Question | Typical tool | SHAIDA |
|---|---|---|
| Who decides? | the model | a human; the model only orders |
| Can the model abstain? | rarely | always, and abstention is tested |
| Can the model author a sentence about evidence? | usually | **never** — explanations are template-filled from deterministic findings |
| What happens when it is wrong? | a false accusation is possible | a queue is mis-ordered; nothing else |

### 4.3 Provenance that is demonstrated, not claimed

The tamper-evidence claim is backed by tests that open the database and alter it **behind the
application's back**, then assert that verification fails and names the row. An earlier version of
this code trusted the stored digest — a real hole, since editing payload and digest together would
pass. The fix was to re-hash the stored payload on every verification. Recording that flaw is part
of the differentiation: this is a claim that invites scrutiny, and we ran the scrutiny ourselves.

### 4.4 Privacy as architecture

There is no field for a reporter's identity, so there is nothing to leak. Aggregates are
**suppressed entirely** below a k-anonymity floor rather than rounded, because rounding leaks by
subtraction. Sensitive categories change *handling*, never the verdict.

### 4.5 Honest evaluation, including a rejected heuristic

The evaluation reports **two** precision numbers where they diverge and explains why, quotes the
conservative one as the headline, and keeps a **rejected** heuristic (49 % over-fire) permanently
measured so it cannot be quietly reintroduced. A judge can re-run one command and get the same
numbers.

### 4.6 It fits the briefs rather than fighting them

The competition's hardest constraints are prohibitions: no live systems, no verdicts, no identity
collection, no auto-removal of speech, no fraud accusations. Most of these are things a team is
tempted to work around. SHAIDA is built so that those constraints are the *architecture*, which
means it cannot drift out of compliance without failing a test.

## 5. Summary

| Dimension | Conventional approach | SHAIDA |
|---|---|---|
| Source of truth | a model | a deterministic rule engine |
| Role of AI | decides | orders and shortlists, may abstain |
| Evidence | shown | hashed, chained, and re-verified from stored data |
| Reporter | identified | no identity field exists |
| Queue | chronological | harm-ranked with a published, itemised score |
| Output | a verdict | a question for a named human, with a required reason |
| Evaluation | a claimed accuracy | a reproducible run with a rejected heuristic recorded |
