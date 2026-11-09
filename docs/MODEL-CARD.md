# Model / System Card: SHAIDA

*Follows the official `docs/05_templates/MODEL_CARD.md` structure.*

## Summary

SHAIDA is a **system**, not a single model. It is a citizen-facing electoral-evidence and
human-triage prototype. Version 1.0.0, built 2026-11-09.

Two small statistical components exist, and both are deliberately subordinate to a deterministic
core:

| Component | Type | Library | Purpose |
|---|---|---|---|
| Severity assist | multinomial logistic regression | scikit-learn `LogisticRegression` | suggest a severity to **order a queue** |
| Claim matcher | character n-gram TF-IDF + cosine similarity | scikit-learn `TfidfVectorizer` / `cosine_similarity` | return a **shortlist** of similar archived claims |

Neither component is a decision-maker, and neither is required for the system to function. Both
train or fit locally, at runtime, from the loaded synthetic data. **No model is downloaded, no API
is called, and no credential is needed.**

## Intended use

**Primary users:** citizen observers, accredited observers and CSO monitors, fact-checkers and
journalists, human reviewers, and election administrators/auditors checking provenance.

**Intended tasks:**

- capture an electoral incident with cryptographic evidence hygiene;
- surface arithmetic and consistency contradictions in result records **for a human to resolve**;
- order a queue of reports by harm so scarce reviewer attention goes to the riskiest first;
- group duplicate reports; shortlist similar archived claims; re-verify that a record was not
  altered.

**Out-of-scope uses (explicitly refused):**

- declaring results, winners, or fraud;
- assessing the truth of a claim or the guilt of a person;
- persuasion, voter microtargeting, or any partisan use;
- profiling individuals or collecting reporter identity;
- automated enforcement or sanction of any kind;
- any connection to a live electoral system.

## Training and data

| Item | Severity assist | Claim matcher |
|---|---|---|
| Data | Official synthetic incident pack (400 narratives) | Official synthetic claim archive (300 claims) |
| Split | deterministic 300 train / 100 test | no training; fit on all, evaluate on 25 % deterministic paraphrase sample |
| Languages | en (pack is English; features are lexical) | en + pcm in the archive |
| Licences | organisers' synthetic pack (CC BY 4.0) | same |
| Synthetic vs real | **100 % synthetic** | **100 % synthetic** |

See [`DATASHEET.md`](DATASHEET.md). **No real election data and no personal data are used.**

## Evaluation

**Severity assist** (held-out, 100 unseen incidents):

| Slice | n | Exact accuracy | Within-one | Notes |
|---|---|---|---|---|
| All | 100 | 0.400 | 0.880 | majority-class baseline: 0.250 / 0.710 |

**Rule engine** (deterministic core, for context — evaluated against the organisers' held-out
labels over 900 records):

| Slice | n | Precision | Recall | F1 | Notes |
|---|---|---|---|---|---|
| All rules | 900 | 0.500 | 0.976 | 0.661 | strict single-label matching |
| Structural tier | 900 | 0.460 | 1.000 | — | 100 % of findings substantiated (63/63) |
| Advisory tier | 900 | 0.632 | 1.000 | — | labelled advisory in the UI |

**Claim matcher** (75 deterministic paraphrases):

| Slice | n | Top-1 | Top-3 | Notes |
|---|---|---|---|---|
| Archive paraphrase | 75 | 0.707 | 0.867 | abstention tested separately |

No confidence intervals are claimed: the test sets are small (100 and 75 items) and a formal CI
would imply more precision than the sample supports. Test-set construction, the label mapping, and
leakage checks are documented in [`../evaluation/DATASET-METHODOLOGY.md`](../evaluation/DATASET-METHODOLOGY.md).

## Error analysis

| Failure mode | Example | Consequence | Who bears it |
|---|---|---|---|
| `R3` false positive | two tallies coincidentally differ by an adjacent swap | a reviewer spends time on a benign record | reviewer time |
| `R3` false negative | the pack's single `digit_transposition` case is a single-digit *substitution*, not an adjacent swap, so R3 does not fire | one labelled anomaly missed | recall |
| `R2` counted as false positive | a record labelled `digit_transposition` also has arithmetic that does not close; R2 reports it correctly, but strict single-label scoring counts it as an FP | depressed headline precision | none in practice — the finding is true |
| Severity assist error | a reporter's framing is genuinely ambiguous | queue ordering is slightly wrong | none — it cannot create a finding |

The two `R3` rows are a genuine weakness and are reported as such in
[`../evaluation/RESULTS.md`](../evaluation/RESULTS.md) §2.2. A false positive costs reviewer time; a
false negative means one anomaly is not surfaced. **Neither can cause a person to be accused**,
because the system never makes an accusation.

## Fairness and bias

- **Tested languages:** the severity assist's features are lexical and were evaluated on English
  pack data only. The claim matcher's archive contains English and Nigerian Pidgin.
- **Not tested:** performance by region, gender, disability, or on Hausa/Yoruba/Igbo text. The
  interface *strings* are translated, but the *assistive model* has not been evaluated on
  non-English input. **This is a real gap and is stated, not hidden.**
- **Mitigation in place:** the assistive components may abstain, and they never create a finding —
  so a language bias in the assist cannot become an accusation. It can only mis-order a queue.
- **Known synthetic-data artefact:** the incident pack is machine-generated and unusually
  repetitive, so clustering's 95.8 % queue reduction is an **upper bound**.

## Uncertainty and abstention

| Component | Confidence | Threshold | On low confidence |
|---|---|---|---|
| Severity assist | top class posterior | 0.55 | returns `None` — **abstain**; the caller must not read this as severity 0 |
| Claim matcher | best cosine similarity | 0.45 | returns the candidates **and** flags abstention; below 0.35 it returns nothing |

Abstention is tested rather than assumed:
`test_severity_assist_abstains_when_the_posterior_is_flat`,
`test_severity_assist_abstains_when_untrained`,
`test_severity_assist_abstains_when_training_data_is_too_small`,
`test_matcher_abstains_on_unrelated_text`,
`test_matcher_abstains_when_below_the_floor_even_with_a_weak_match`,
`test_empty_archive_abstains_rather_than_crashing`.

## Human oversight

- **Who reviews:** a human reviewer works the harm-ranked queue. There is no automated path by
  which a report is resolved.
- **Override mechanism:** `POST /v1/reports/{id}/review` records a decision **and a mandatory
  reason** (`test_review_requires_a_reason`); an unknown decision value is rejected
  (`test_review_rejects_unknown_decision`).
- **Audit log:** the decision and its reason are appended to the same hash-chained log
  (`test_review_is_recorded_and_audited`), which anyone can re-verify.
- **Explanations are not model-generated.** They are template-filled from deterministic findings,
  so a sentence about someone's evidence can never be invented.
- **Verdict language is blocked at runtime** by `taxonomy.assert_no_verdict_language()`, asserted
  across every language and across the whole API surface.

## Ethical and legal considerations

- **Nonpartisan by construction:** no candidate or party entity exists in the schema; there is no
  channel to reach a voter, so microtargeting is architecturally impossible.
- **Data protection:** identity-free schema, location coarsened, k-anonymity suppression, NDPA 2023
  alignment. A formal DPIA is a **precondition for real use**, not a completed step. See
  [`DATA-PROTECTION.md`](DATA-PROTECTION.md).
- **Electoral law:** the tool makes no determination about any election matter; it produces
  questions for humans. It is not connected to any live system.
- **Misuse risk:** the main misuse risk is a bad actor filing false reports to flood a queue.
  Mitigations: per-client rate limiting, duplicate clustering, and the fact that nothing is
  published automatically — every report waits for a human.
- **Winning is not approval.** Stated in [`SAFETY-AND-LIMITATIONS.md`](SAFETY-AND-LIMITATIONS.md) §6
  and in the application itself.

## Maintenance

- **Monitoring:** none automated; the prototype has no telemetry and sends no data anywhere.
- **Retraining plan:** the severity assist retrains from loaded data on every start. Any future
  model addition must keep the three rules: it may not conclude, it must be able to abstain, and
  it may not author explanations.
- **Reporting issues:** raise an issue in the repository.
- **Version:** 1.0.0. Superseded versions are not deployed anywhere.
