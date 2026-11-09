# AI methodology

## 0. The governing constraint

Most "AI for elections" tools fail the same way: the model is placed where its output *is* the
conclusion. SHAIDA inverts that. The question this document answers is not "what model do we use"
but **"where is a model allowed to sit, given that a wrong answer must never become an
accusation?"**

The answer is a strict three-tier placement.

| Tier | Who decides | May a model live here? |
|---|---|---|
| **Deterministic core** — rules, hash chain, triage weights, clustering, privacy floor, templates | arithmetic and fixed rules | **No model. Ever.** This is the source of truth. |
| **Assistive layer** — severity suggestion, claim shortlisting | a small model | **Yes**, but it may only order, shortlist or suggest, and it must be able to abstain. |
| **Decision layer** — is this true, is this fraud, what is the result | a named human | **No model. There is no automated decision path in the system.** |

Everything below follows from this placement.

---

## 1. Why the AI is small, and why that is the point

An "election AI" that uses a large language model to judge claims has three problems:

1. **It is unaccountable.** A fluent sentence carries no trace of which evidence produced it.
2. **It is unfalsifiable.** You cannot re-check a probability with a pen.
3. **It is unsafe.** A confident wrong answer about an election is a public harm, not a bug.

SHAIDA therefore uses the *smallest* models that do useful work, in the places where being wrong
is harmless:

- a **multinomial logistic regression** over transparent lexical features, to suggest a severity;
- a **character n-gram TF-IDF retriever**, to shortlist similar archived claims.

Neither downloads a model, calls an API, or needs a credential. Both run offline. Both abstain.

---

## 2. Component 1 — Severity assist

### 2.1 What it is

A multinomial logistic regression (`scikit-learn`, `class_weight="balanced"`) that estimates the
**reported severity band (0–4)** of an incident narrative.

### 2.2 Why it exists

In the harm-ranked queue, `severity` carries the largest weight (0.35). But a reporter is allowed
to leave severity unstated — and often does, because asking someone to rate their own experience on
a five-point scale is a bad question. The assist fills that gap **for ordering purposes only**.

### 2.3 Features (all transparent, all inspectable)

| Feature | Meaning |
|---|---|
| cue counts per severity class | frequency of severity-indicative phrases, normalised by length |
| modifier counts | intensifiers and mitigators |
| `min(1, tokens/60)` | how much detail the reporter gave |
| negation density | how often negation appears, normalised by length |

There are no embeddings and no opaque features. Every input to the model is a count a human could
recompute.

### 2.4 Training

- Trained **locally, on the fly**, from the official synthetic incident pack (300 train / 100
  deterministic test split).
- **Disables itself** if there are fewer than 40 training rows or fewer than 2 distinct classes.
  A missing model must never silently degrade into an unvalidated heuristic.
- Reports `trained_on` and `train_accuracy` so its provenance is visible.

### 2.5 Abstention — the core safety property

`predict()` returns `(None, confidence, detail)` when the top posterior is **below 0.55**.
`None` means *abstained* — and critically, the caller must **not** treat it as a severity of zero.
That distinction is tested:

- `test_severity_assist_abstains_when_untrained`
- `test_severity_assist_abstains_when_training_data_is_too_small`
- `test_severity_assist_abstains_when_the_posterior_is_flat`
- `test_severity_assist_learns_and_reports_its_training_size`

The interface shows the abstention honestly: an item reads `assist: abstained (43%)`, not a
fabricated number.

### 2.6 Measured performance

| Measure | Model | Majority-class baseline |
|---|---|---|
| Exact accuracy (held-out) | 0.400 | 0.250 |
| Within-one accuracy | 0.880 | 0.710 |

The absolute numbers are modest **and this is reported as modest, not spun**. The signal — a
reporter's own framing of seriousness — is genuinely weak, and the model is honest about that.
What matters operationally is that it beats the baseline and that it abstains instead of guessing.

### 2.7 What it may never do

It may not create a finding, change a finding, or alter a flag. Its output is one of six inputs to
a published weighted sum that **orders a queue**. Nothing else.

---

## 3. Component 2 — Claim matcher

### 3.1 What it is

A character n-gram TF-IDF retriever (`analyzer="char_wb"`, 3–5 grams, `sublinear_tf=True`) over a
fact-check archive, ranked by cosine similarity.

### 3.2 Why character n-grams

The official brief names robustness to **typos, paraphrase and code-switching** as success
criteria. Word-level matching breaks on all three. Nigerian claim text mixes English, Pidgin,
Hausa, Yoruba and Igbo, often in one message; character n-grams survive that mixing without a
multilingual model, without a download, and without a credential.

### 3.3 The output is a shortlist, not a verdict

`match()` returns up to `top_k` matches, each carrying the archive entry's **prior reviewer
label** — never a new label computed by SHAIDA. The tool shows a fact-checker what a human already
concluded about a similar claim; it does not conclude anything itself.

### 3.4 Two abstention gates

1. **No match above `min_similarity` (0.35)** → abstain: *"no archived claim is similar enough;
   treat this as new and route to a human."*
2. **Best match below `abstain_below` (0.45)** → return the candidates *and* abstain: *"closest
   archive match is only 0.39 similar, below the 0.45 abstention floor; a human must decide whether
   it really is the same claim."*

The second gate is the important one: it shows the candidate **and** refuses to assert it, which is
the honest behaviour when a model is uncertain but not empty-handed.

### 3.5 Measured performance

| Measure | Value |
|---|---|
| Archive size | 300 |
| Evaluated (25 % deterministic sample) | 75 |
| Top-1 accuracy | 0.707 |
| Top-3 accuracy | 0.867 |
| Abstention rate | 0.000 |

**Read the zero abstention rate carefully.** Every evaluation query is a deterministic paraphrase
of a real archive entry, so a match always exists and the floor is never hit. This is therefore
**not** evidence that abstention works — it is evidence that retrieval works. Abstention is tested
separately, on unrelated text:
`test_matcher_abstains_on_unrelated_text`,
`test_matcher_abstains_when_below_the_floor_even_with_a_weak_match`,
`test_empty_archive_abstains_rather_than_crashing`.

### 3.6 What it may never do

It may not label a claim true or false. It has no truth model at all — only a similarity model and
a lookup of prior human labels.

---

## 4. Component 3 — Deterministic clustering (not AI, listed for completeness)

Near-duplicate incident reports are grouped by normalised similarity gated on category, so a
reviewer sees *one* item with a count instead of fifty entries. Measured on the official synthetic
incident pack: 400 reports → 17 clusters (95.8 % queue reduction).

**This is an upper bound.** The synthetic pack is machine-generated and unusually repetitive; real
incident narratives vary far more, so the achievable reduction in the field would be lower. The
figure demonstrates the mechanism; it does not predict real savings.

---

## 5. Why there is no language model in the explanation path

Every reviewer explanation and every citizen-facing sentence is **assembled from fixed templates
filled with deterministic findings** — never generated by a language model. The About page states
this in the same words.

The reason is narrow and specific: a language model could author a fluent sentence *about
someone's evidence* that is not grounded in any computed fact. That is exactly the failure mode
this project exists to avoid. A template cannot invent a contradiction that the arithmetic did not
find.

The multilingual dimension (en, pcm, ha, yo, ig) is handled by **translated templates**, not by
machine translation at runtime — so a sentence shown to a reviewer is a reviewed string, not a
generated one. The About page is explicit that the Hausa, Yoruba and Igbo strings are first-pass
translations pending native-speaker review.

---

## 6. Enforced honesty: the verdict-language guard

`taxonomy.assert_no_verdict_language()` raises `VerdictLanguageError` if any generated text
contains forbidden verdict vocabulary (`fraudulent`, `corrupt`, `falsified`, and others). It is:

- called on generated explanations at build time,
- asserted in `test_no_finding_uses_verdict_language`,
- asserted across all five languages in
  `test_explanations_exist_in_every_supported_language_and_avoid_verdicts`,
- asserted across the whole API surface in `test_no_api_response_uses_verdict_language`.

This turns "we promise not to declare verdicts" into a runtime property that fails loudly if
violated.

---

## 7. Deterministic rule engine — the actual source of truth

Not AI, and documented in full in `docs/TECHNICAL-ARCHITECTURE.md` §5. Summarised here because it
is what makes the AI safe:

- **Structural tier** (arithmetic contradictions): R1 accredited > registered, R2 sheet totals do
  not close, R5 tallies duplicated from the previous unit.
- **Advisory tier** (statistical hints): R3 adjacent-digit swap, R4 round-number pattern, R6 robust
  turnout outlier (median/MAD), R7 negative/impossible values.

Measured against the organisers' held-out labels: **recall 97.6 %**, **flag rate 5.4 %**,
**clean-record false-alarm rate 0.8 %**, and **100 % structural substantiation (63/63)** — every
structural finding's stated contradiction actually holds.

Two design decisions worth naming:

- **R6 uses median/MAD, not mean/σ**, because a mean/σ outlier test is itself dragged by the
  outliers it is meant to find. It abstains on a degenerate cohort instead of dividing by zero.
- **A tempting broad digit heuristic was measured and rejected.** Flagging two tallies that differ
  in exactly one digit fires on **49 %** of records. It is kept permanently measured in the
  evaluation harness and asserted rejected in `test_evaluation_guards.py`, so it cannot be quietly
  reintroduced.

---

## 8. Summary of what is measured vs. what is claimed

| Claim | Measured? | Where |
|---|---|---|
| Rule engine recall / precision / flag rate | yes | `evaluation/RESULTS.md` §1 |
| Structural findings are true | yes (63/63) | `evaluation/RESULTS.md` §2.1 |
| Severity assist beats baseline | yes (held-out) | §2.6 above |
| Claim matcher top-3 | yes | §3.5 above |
| Clustering reduction | yes, but an **upper bound** | §4 above |
| Triager surfaces serious items first | yes (+2.08 lift) | `evaluation/RESULTS.md` §4.4 |
| Real-world accuracy on Nigerian election data | **No — not claimed** | stated as a limitation |
| Reviewer agreement with flags | **No — not measured** | stated as a limitation |
| Behaviour at national scale | **No — not tested** | stated as a limitation |

The last three rows are the ones a judge should hold us to. They are limitations, not omissions.
