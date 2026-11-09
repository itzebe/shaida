# Evaluation Report: SHAIDA

*Follows the official `docs/05_templates/EVALUATION_REPORT_TEMPLATE.md` structure.*

---

## 1. Objective and success criteria

**Objective.** Demonstrate that a deterministic, privacy-preserving evidence-and-triage pipeline
can surface genuinely verifiable electoral-data contradictions at high recall and a reviewable flag
rate, while **never** declaring a verdict — and that every number is reproducible.

**Success criteria**, derived from the Track 2 and Track 5 briefs:

| Criterion | Target | Result |
|---|---|---|
| Catch labelled anomalies | high recall | **97.6 %** |
| Keep the flag rate reviewable by humans | small fraction | **5.4 %** |
| Do not flag clean records | low false-alarm | **0.8 %** |
| Every structural finding must be true | 100 % | **100 %** (63/63) |
| Assistive components must abstain when unsure | enforced | enforced + tested |
| No output may declare a verdict | absolute | enforced at runtime + tested |

## 2. Test data

- **Source:** the organisers' official synthetic starter pack — `results_synthetic.csv` (900
  records) with `anomaly_labels_HELD_OUT.csv` as the answer key.
- **Size:** 900 records; 42 labelled anomalous.
- **Split:** none needed for the rule engine — rules are fixed and applied to all 900, so there is
  no train/test leakage. The severity assist uses a deterministic 300/100 split; the claim matcher
  uses a deterministic 25 % (`index % 4 == 0`) sample of the archive.
- **Held-out guarantee:** the label file is the organisers' and was never used to tune a rule. The
  label→rule mapping is declared up front in
  [`DATASET-METHODOLOGY.md`](DATASET-METHODOLOGY.md) §4, so any reader can change one line and see
  the numbers move.
- **Leakage checks:** none of the rules reference the label column; the evaluation script loads
  labels only after the rules have run.

## 3. Baselines

| Component | Baseline | Why it is the right baseline |
|---|---|---|
| Severity assist | majority-class ("always predict the most common training severity") | correct honest bar for an ordinal classifier |
| Rule engine | *no baseline needed* — the engine is deterministic and is scored directly against the held-out labels | — |
| A rejected heuristic | "flag two tallies differing in exactly one digit" | measured, then **rejected** at 49 % over-fire |

## 4. Results

### 4.1 Rule engine — overall (strict single-label matching)

| | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| All rules | 41 | 41 | 1 | 0.500 | 0.976 | 0.661 |

### 4.2 By tier

| Tier | TP | FP | Precision | Recall |
|---|---|---|---|---|
| Structural | 29 | 34 | 0.460 | 1.000 |
| Advisory | 12 | 7 | 0.632 | 1.000 |

### 4.3 Per rule

| Rule | Tier | TP | FP | Precision | Recall |
|---|---|---|---|---|---|
| `R1_accredited_exceeds_registered` | structural | 16 | 0 | 1.000 | 1.000 |
| `R2_sum_mismatch` | structural | 8 | 34 | 0.190 | 1.000 |
| `R3_digit_transposition` | advisory | 0 | 7 | 0.000 | 0.000 |
| `R4_suspicious_round_numbers` | advisory | 12 | 0 | 1.000 | 1.000 |
| `R5_duplicated_from_previous_unit` | structural | 5 | 0 | 1.000 | 1.000 |

### 4.4 The honest correction to headline precision

The pack assigns **one primary label per record**. A record labelled `digit_transposition` can also
have arithmetic that does not close; `R2` correctly reports that, and strict scoring counts the
correct extra finding as a false positive. Measured directly: **every one of `R2`'s firings states a
contradiction that holds in the record's own numbers** — substantiation **63/63 = 100 %**.

We therefore report **both** numbers and quote the conservative one as the headline. We do not
claim the substantiation rate as precision.

### 4.5 Confidence intervals and ablations

No confidence intervals are claimed: with 42 positives, an interval would be wide and would imply
more precision than the sample supports. Ablations were performed informally during development
(notably the rejected single-digit heuristic in §3) and are recorded rather than presented as a
formal study.

### 4.6 Assistive components

| Component | Measure | Value | Baseline |
|---|---|---|---|
| Severity assist (held-out, n=100) | exact accuracy | 0.400 | 0.250 |
| | within-one accuracy | 0.880 | 0.710 |
| Claim matcher (n=75) | top-1 | 0.707 | — |
| | top-3 | 0.867 | — |

### 4.7 Throughput

900 records in ~0.10 s — **~9 000–9 600 records/second** depending on machine load. The rule engine is pure integer arithmetic with
no I/O and no model inference on the hot path.

## 5. Human-in-the-loop impact

- **Alerts per 1 000 records:** 54 (from the 5.4 % flag rate) — a reviewable volume, which is the
  point of the flag-rate target.
- **Queue reduction from clustering:** 400 → 17 (95.8 %). **Stated as an upper bound** — the
  synthetic pack is unusually repetitive, so real savings would be lower.
- **Triage lift:** the most serious decile has a mean severity of 4.00 against 1.93 for the rest —
  a **+2.08** lift, so scarce attention reaches the riskiest reports first.
- **Reviewer time saved / agreement with human labels:** **not measured.** No human-factors study
  was run, and we do not estimate one. This is the largest gap in this evaluation and it is stated
  in §10.

## 6. Robustness

| Dimension | Status |
|---|---|
| Typos | The claim matcher is character n-gram based and tested to survive a one-character error (`test_matcher_survives_typos`, `test_jaccard_tolerates_a_small_typo`) |
| Code-switching | Tested with Nigerian Pidgin phrasing (`test_matcher_handles_pidgin_phrasing`) |
| Paraphrase | The claim-matcher evaluation *is* a paraphrase task (rotation + character drop) |
| Low bandwidth | The app shell is cached by a service worker that never caches API responses, so it works offline; the UI is a static build with no framework dependency |
| Adversarial examples | Rule-level: negative and impossible values are rejected at the boundary and caught by `R7`; `test_r3_silent_on_non_adjacent_permutation` stops the digit rule degrading into a broad permutation test; malformed input returns 422 with a stable shape |
| Degenerate input | The turnout outlier test abstains on a zero-spread cohort rather than dividing by zero; the matcher abstains on an empty archive rather than crashing |

## 7. Usability and accessibility testing

- **Automated accessibility:** axe-core, WCAG 2.0/2.1/2.2 A + AA, across 6 pages × 2 viewports
  (desktop 1440 px, mobile 390 px) → **0 violations**. This found and fixed two real defects: an
  unlabelled file input, and two contrast pairs below 4.5:1.
- **Responsive:** 6 pages × 4 viewports (1440, 834, 390, 320 px) → **0 horizontal overflows**. This
  found and fixed three real defects (grid `minmax()` floors, a fieldset's `min-inline-size`, and a
  file input's intrinsic width).
- **Runtime errors:** 24 page/viewport combinations → 0 console or page errors.
- **Participants:** **none.** No user testing with real participants was conducted, and none is
  claimed. Automated checks are not a substitute for testing with assistive-technology users, which
  is listed as a precondition for real use.

## 8. Failure cases, with examples and fixes attempted

1. **`R3` misses the pack's transposition case.** The pack's single `digit_transposition` record
   (`SIM-00087`, tallies `{A:114, B:501, C:69, D:68, E:21}`) is a single-digit *substitution*
   (68→69), not an adjacent swap. `R3` correctly does not fire. Fix attempted: widen `R3` to catch
   substitutions. **Rejected** — the widened rule fires on 49 % of records. Documented, measured,
   and locked by `test_adjacent_swap_rule_does_not_degrade_into_a_broad_permutation_test`.
2. **`R2` false positives under strict scoring.** Cause: single-primary-label labelling. Mitigation:
   report the substantiation rate alongside precision; do not claim it as precision.
3. **A runtime crash the build did not catch.** `ReportPage.jsx` used an `online` prop that was
   never passed. Type-checking and the build both passed; the browser run caught it. Fixed by adding
   the default. *Lesson recorded: a successful build is not evidence a page works.*
4. **Three CSS overflow defects** and **two accessibility defects** invisible to the build and to
   the backend suite, caught only by the browser checks. All fixed and re-verified.

## 9. Reproducibility

```bash
# backend
cd backend && python -m pytest tests -q          # 111 passed, 2 warnings
# evaluation
python evaluation/evaluate.py                    # rewrites evaluation/results.json
# frontend
cd frontend && npm run build                     # clean build
```

- **Seeds:** none — the pipeline is deterministic and single-threaded; the 75/25 split and the 25 %
  sample are index-based, not random.
- **Environment:** Python 3.13, Node 18+. No GPU, no external service, no credential.
- **Runtime:** the evaluation completes in well under a second.

## 10. Conclusion and next steps

The deterministic core does what it claims: high recall, a reviewable flag rate, a very low
clean-record false-alarm rate, and **every structural finding true**. The assistive layer is small,
honest about its weakness, and can never turn a wrong answer into an accusation.

**What would be needed to validate in a real setting:**

1. **Human-factors study** — do reviewers agree with flags, and how long does review take?
2. **Real-world data validation** under the NDPA, with proper consent and ethics review, to replace
   synthetic-data estimates with real ones.
3. **Linguistic fairness evaluation** on Hausa, Yoruba and Igbo incident text.
4. **Adversarial and load testing** at a scale this prototype has not been tested at.
5. **Independent security review** of the API and the hash chain.

Until those exist, the honest position is the one stated on every page of the application:
**SHAIDA is a working prototype, it flags and does not judge, and it is not approved for
operational electoral deployment.**
