# Evaluation results

Every number in this file is produced by running `python evaluation/evaluate.py` and is stored
verbatim in [`results.json`](results.json). Nothing here is hand-entered. Where a number is
weak, it is reported as weak and the reason is given.

Run date and environment: this repository's backend virtual environment, Python 3.13,
deterministic single-threaded execution.

## 0. Headline

| Measure | Value |
|---|---|
| Labelled anomalies detected (recall) | **41 / 42 = 97.6 %** |
| Records flagged, out of 900 | 49 (**5.4 %**) |
| Clean records wrongly flagged | 7 / 858 (**0.8 %**) |
| Structural findings that are genuinely true | **63 / 63 = 100 %** |
| Throughput | ~9 000–9 600 records/second |

Read together: the engine catches nearly every labelled anomaly, flags a small and reviewable
share of the corpus, and almost never flags a clean record. That combination — not recall alone —
is what makes a flag queue usable.

## 1. Deterministic rule engine

Evaluated against the organisers' held-out label file. The label mapping is declared in
[`DATASET-METHODOLOGY.md`](DATASET-METHODOLOGY.md) §4.

### Overall, strict label matching

| | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| All rules | 41 | 41 | 1 | 0.500 | 0.976 | 0.661 |

### By tier

| Tier | TP | FP | Precision | Recall |
|---|---|---|---|---|
| Structural (arithmetic contradictions) | 29 | 34 | 0.460 | 1.000 |
| Advisory (statistical hints) | 12 | 7 | 0.632 | 1.000 |

### Per rule

| Rule | Tier | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|---|
| `R1_accredited_exceeds_registered` | structural | 16 | 0 | 0 | **1.000** | **1.000** |
| `R2_sum_mismatch` | structural | 8 | 34 | 0 | 0.190 | 1.000 |
| `R3_digit_transposition` | advisory | 0 | 7 | 1 | 0.000 | 0.000 |
| `R4_suspicious_round_numbers` | advisory | 12 | 0 | 0 | **1.000** | **1.000** |
| `R5_duplicated_from_previous_unit` | structural | 5 | 0 | 0 | **1.000** | **1.000** |

## 2. Interpreting the two low numbers honestly

### 2.1 `R2_sum_mismatch`: precision 0.190 under strict matching, 1.000 in substance

The official pack assigns **one primary label per record**. A record labelled, say,
`digit_transposition` can *also* have arithmetic that does not close, and R2 correctly reports
that. Strict scoring counts the correct extra finding as a false positive.

Measured directly: **every one of R2's 42 firings states a contradiction that holds in the
record's own numbers** — 42/42, no exceptions. The engine is not wrong about the arithmetic; the
strict metric is counting a true statement as a miss because the pack only has room for one label.

We report the conservative 0.190 as the headline and the 1.000 substantiation alongside it. We
do not claim the higher number as precision.

### 2.2 `R3_digit_transposition`: precision 0.000 and recall 0.000

This rule performs badly on this pack, and the reason is concrete rather than mysterious.

- The pack contains **exactly one** `digit_transposition` record: `SIM-00087`, with tallies
  `{A:114, B:501, C:69, D:68, E:21}`.
- R3 detects **adjacent digit swaps** (1243 vs 1234). The pack's case is a single-digit
  **substitution** (68 vs 69), which is a different typo signature. R3 correctly does not fire.
  Hence recall 0.
- R3 fired 7 times elsewhere, on coincidental adjacent-swap pairs. Every one is a false positive.
  Hence precision 0.

**This is a real limitation and we are not hiding it.** Two options existed:

1. Widen R3 to catch single-digit substitutions as well.
2. Leave R3 narrow and accept the miss.

We tried option 1, measured it, and **rejected it**. See §4. A broad digit rule flags 49 % of the
corpus, which would destroy the queue. Missing one synthetic case is a far better outcome than
burying 444 clean records in noise.

R3's 7 false positives remain a genuine weakness. The rule is advisory-tier, contributes a
severity of 1, and carries the sentence "can also occur by chance" in its own message, but the
honest statement is that on this pack it earned nothing. A future version should raise its
threshold or require corroboration from another signal.

## 3. Rejected heuristic, measured

| Heuristic | Records flagged | Fire rate | Status |
|---|---|---|---|
| Flag two tallies differing in exactly one digit | 444 / 900 | **49.3 %** | **rejected** |

This is kept in the evaluation harness as a permanent guard
(`REJECTED_HEURISTICS` in `evaluation/evaluate.py`, asserted in
`backend/tests/test_evaluation_guards.py`) so it can never be quietly reintroduced. The official
brief warns that over-firing heuristics are the classic failure of this kind of tool; here is the
number that proves it.

## 4. Assistive AI components

### 4.1 Severity assist (held-out)

Trained on 300 incidents, scored on 100 unseen ones.

| Measure | Model | Majority-class baseline |
|---|---|---|
| Exact accuracy | 0.400 | 0.250 |
| Within-one accuracy | 0.880 | 0.710 |

The model beats the baseline on both measures. The absolute numbers are modest, and that is the
honest result: the reported severity is the *reporter's own framing*, which is a genuinely weak
signal. The component is used only to order a queue, never to make a finding, and it abstains
rather than guessing when its posterior is flat (tested in `test_assist.py`).

### 4.2 Claim matcher

| Measure | Value |
|---|---|
| Archive size | 300 claims |
| Evaluated (25 % deterministic sample) | 75 |
| Top-1 accuracy | 0.707 |
| Top-3 accuracy | 0.867 |
| Abstention rate | 0.000 |

Method: each claim is re-worded deterministically (rotate the words, drop one character) and the
matcher must recover the original. Top-3 is the operationally relevant number, since the tool
presents a shortlist to a human rather than an answer.

The zero abstention rate here is expected — every query is a paraphrase of a real archive entry —
and it is **not** evidence that abstention works. Abstention is tested separately, on unrelated
text, in `backend/tests/test_assist.py::test_matcher_abstains_on_unrelated_text` and
`test_matcher_abstains_when_below_the_floor_even_with_a_weak_match`.

### 4.3 Incident clustering

| Measure | Value |
|---|---|
| Reports | 400 |
| Clusters | 17 |
| Queue items saved | 383 (95.8 % reduction) |

**This number is an upper bound and should be read with care.** The official synthetic incident
pack is machine-generated and contains many near-identical narratives, so grouping succeeds
unusually well. Real incident reports vary far more in wording, and the achievable reduction on
real data would be lower. The figure demonstrates that the mechanism works; it does not predict
real-world savings.

### 4.4 Harm-ranked triage ordering

| Measure | Value |
|---|---|
| Mean severity of the top decile | 4.00 |
| Mean severity of the rest | 1.93 |
| Lift | **+2.08** |

The published weighted model surfaces markedly more serious reports first. Severity is only one
of six signals, so the ranking is not expected to reproduce severity exactly; the lift shows the
ordering is doing real work.

## 5. Performance

| Measure | Value |
|---|---|
| Records processed | 900 |
| Wall time | 0.094 s |
| Throughput | ~9 000–9 600 records/second (varies with machine load) |

The rule engine is pure integer arithmetic over in-memory records with no I/O and no model
inference on the hot path, which is why it is fast. The assistive model is only consulted when a
reporter has not stated a severity.

## 6. What these results do not establish

- **No real-world accuracy claim.** The pack is synthetic. A score against it is not an estimate
  of performance on real polling-unit returns.
- **No claim that the injected anomalies resemble real manipulation**, only that they match the
  organisers' definitions.
- **No human-factors evidence.** We have not measured whether a reviewer agrees with a flag or
  how long review takes.
- **No scale evidence.** 900 records is small; national scale, concurrency and adversarial load
  are untested.
- **`R3` is a genuine weak point** and is reported as such rather than excused.

## 7. Reproduce

```bash
python evaluation/evaluate.py          # rewrites results.json
pytest backend/tests -q                # 111 tests, incl. evaluation regression guards
```
