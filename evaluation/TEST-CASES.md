# Test cases

The test suite is the evidence that the safeguards are real rather than described. It is not
decorative: several tests exist specifically to prove a *negative* — that the system cannot do
something it must not do.

Run it:

```bash
cd backend && python -m pytest tests -q
# 111 passed, 2 warnings  (the two warnings are Starlette/httpx deprecation notices)
```

Six modules, grouped by the property they protect.

---

## 1. `test_rules.py` — the deterministic engine (25 tests)

Protects: a flag means exactly what it says, and a clean record stays clean.

| Test | What it proves |
|---|---|
| `test_clean_record_produces_no_findings` | A well-formed record yields zero findings |
| `test_clean_record_checks_every_rule` | All rules are evaluated, not short-circuited |
| `test_r1_fires_and_is_structural` | Accreditation > register is flagged, structural tier |
| `test_r1_does_not_fire_when_equal` | Boundary: equality is not a contradiction |
| `test_r2_fires_when_totals_do_not_close` | The sheet's own arithmetic is checked |
| `test_r2_silent_when_totals_close` | No false flag when arithmetic balances |
| `test_r3_fires_on_adjacent_swap` | Detects a genuine adjacent-digit transposition |
| `test_r3_is_advisory_only` | R3 never claims structural weight |
| `test_r3_silent_on_non_adjacent_permutation` | Does not degrade into a broad permutation test |
| `test_r3_silent_on_identical_values` | Identical tallies are not a transposition |
| `test_r4_fires_on_three_round_tallies` | Round-number pattern flagged as advisory |
| `test_r4_silent_on_two_round_tallies` | Threshold holds |
| `test_r5_fires_when_tallies_repeat_the_previous_unit` | Duplicated sheet detected |
| `test_r5_does_not_fire_on_the_first_record` | No phantom "previous unit" |
| `test_r6_silent_without_a_cohort` | Outlier test abstains without a peer group |
| `test_r6_fires_on_an_extreme_outlier_in_a_large_cohort` | Robust median/MAD test works |
| `test_r6_falls_back_when_the_cohort_is_degenerate` | Zero-spread cohort handled, not crashed |
| `test_r7_fires_on_negative_tally` / `..._registered` | Impossible values rejected |
| `test_findings_are_ordered_structural_first` | Severity ordering is deterministic |
| `test_certificate_balances_for_a_clean_record` | Arithmetic certificate closes |
| `test_certificate_flags_a_broken_record` | Certificate shows the imbalance |
| `test_implied_registered_floor_is_the_maximum_constraint` | The stated floor is the binding one |
| `test_no_finding_uses_verdict_language` | **No finding text can assert a verdict** |

---

## 2. `test_provenance.py` — tamper-evidence (13 tests)

Protects: the integrity claim is demonstrated, not asserted. This is the module a security
reviewer should read first.

| Test | What it proves |
|---|---|
| `test_content_hash_is_stable_and_order_independent` | Canonical hashing is deterministic |
| `test_content_hash_excludes_derived_metadata` | AI-derived fields cannot alter the evidence hash |
| `test_content_hash_changes_when_content_changes` | Any content edit changes the digest |
| `test_verify_record_accepts_and_rejects` | Verification returns a decision, not a vibe |
| `test_chain_verifies_when_untouched` | The happy path |
| `test_chain_detects_an_edited_entry` | Editing an entry breaks the chain |
| `test_chain_detects_a_deleted_entry` | Deleting an entry breaks the chain |
| `test_chain_detects_reordering` | Reordering entries breaks the chain |
| `test_chain_hash_binds_sequence_number` | Sequence number is inside the hash, so renumbering fails |
| `test_audit_chain_intact_after_appends` | Appending preserves the chain |
| `test_audit_chain_detects_direct_database_tampering` | **Direct SQL edit of a stored row is caught** |
| `test_audit_chain_detects_row_deletion` | Direct SQL deletion is caught |
| `test_audit_chain_is_empty_and_intact_on_a_fresh_store` | Empty store verifies rather than erroring |

The two direct-database tests are the point. Anyone can write "tamper-evident" in a README; these
tests open the database, alter it behind the application's back, and assert that verification
fails and names the altered row.

---

## 3. `test_api.py` — boundary behaviour (22 tests)

Protects: the public surface validates input, leaks nothing, and never speaks in verdicts.

| Group | Tests |
|---|---|
| Honesty | `test_health_declares_no_verdict_capability`, `test_no_api_response_uses_verdict_language` |
| Report lifecycle | `test_create_report_returns_hash_and_reference`, `test_created_report_can_be_retrieved_and_verified` |
| Privacy | `test_no_reporter_identity_is_stored`, `test_coordinates_are_coarsened_and_never_returned_exactly` |
| Sensitive handling | `test_sensitive_category_is_flagged_for_extra_handling` |
| Input validation | `test_invalid_input_is_rejected_with_422`, `test_narrative_over_the_limit_is_rejected`, `test_result_batch_rejects_negative_tally_at_the_boundary` |
| Error hygiene | `test_error_shape_is_stable_and_leaks_nothing`, `test_unknown_report_returns_404` |
| Human review | `test_review_requires_a_reason`, `test_review_rejects_unknown_decision`, `test_review_is_recorded_and_audited` |
| Result checks | `test_result_check_accepts_a_batch_and_flags_arithmetic`, `test_certificate_is_available_for_a_stored_record` |
| Aggregation | `test_aggregation_suppresses_small_cells` |
| Claim matching | `test_claim_match_abstains_on_unrelated_text`, `test_claim_match_rejects_empty_query` |
| Abuse control | `test_rate_limiter_blocks_after_the_limit`, `test_rate_limiter_is_per_client` |

`test_no_reporter_identity_is_stored` is the strongest privacy test: it creates a report and then
asserts that no name, phone number or account field exists anywhere in the stored record.

---

## 4. `test_assist.py` — assistive AI and triage (23 tests)

Protects: every AI component abstains rather than guessing, and the ranking explains itself.

| Group | Tests |
|---|---|
| Matcher | `test_matcher_finds_a_near_duplicate`, `test_matcher_survives_typos`, `test_matcher_handles_pidgin_phrasing` |
| Abstention | `test_matcher_abstains_on_unrelated_text`, `test_matcher_abstains_when_below_the_floor_even_with_a_weak_match`, `test_empty_archive_abstains_rather_than_crashing` |
| Severity assist | `test_severity_assist_abstains_when_untrained`, `test_severity_assist_abstains_when_training_data_is_too_small`, `test_severity_assist_learns_and_reports_its_training_size`, `test_severity_assist_abstains_when_the_posterior_is_flat` |
| Transparent ranking | `test_priority_is_a_weighted_sum_of_published_weights`, `test_priority_always_explains_itself`, `test_sensitive_category_outranks_an_equivalent_routine_one`, `test_higher_severity_ranks_higher`, `test_repeat_reports_raise_priority` |
| Explanations | `test_explanation_for_a_clean_record_states_that_nothing_was_triggered`, `test_explanation_carries_the_findings_own_text`, `test_explanations_exist_in_every_supported_language_and_avoid_verdicts`, `test_unknown_language_falls_back_to_english` |
| Clustering | `test_identical_reports_join_one_cluster`, `test_different_categories_never_share_a_cluster`, `test_clustering_is_deterministic`, `test_unrelated_reports_stay_separate` |

---

## 5. `test_evaluation_guards.py` — regression locks (8 tests)

Protects: the measured quality cannot silently regress, and a rejected heuristic cannot return.

| Test | What it locks |
|---|---|
| `test_recall_stays_high` | Recall floor |
| `test_clean_false_alarm_rate_stays_low` | False-alarm ceiling |
| `test_flag_rate_stays_reviewable` | Flag rate stays inside a human-reviewable band |
| `test_structural_findings_are_substantiated` | Every structural finding still holds arithmetically |
| `test_structural_precision_is_perfect_on_labelled_rules` | R1/R4/R5 stay perfect |
| `test_rejected_heuristic_is_still_measured_and_still_bad` | The 49 %-over-firing heuristic stays rejected |
| `test_adjacent_swap_rule_does_not_degrade_into_a_broad_permutation_test` | R3 stays narrow |
| `test_processing_throughput_is_adequate` | Throughput floor |

These tests make the honest evaluation numbers a *contract*. A future change that improves recall
by flooding the queue will fail here.

---

## 6. `test_text.py` — multilingual normalisation (14 tests)

Protects: Nigerian-language input is handled correctly rather than mangled.

| Test | What it proves |
|---|---|
| `test_yoruba_diacritics_survive_normalisation` | Yoruba tone marks are preserved |
| `test_house_and_igbo_hooks_survive` | Hausa hooked letters and Igbo dotted characters survive |
| `test_pidgin_stopwords_are_dropped` | Pidgin stopwords are handled |
| `test_long_numbers_are_placeholderised` | Long numbers become `<num>`, so two different numbers never collide |
| `test_urls_are_removed` | URLs stripped before matching |
| `test_emphasis_repeats_are_reduced` | "very very good" normalises |
| `test_jaccard_tolerates_a_small_typo` | Similarity is robust to a one-character error |
| `test_empty_input_is_handled_without_error` | Empty input is not an error path |
| *(plus case folding, whitespace collapse, tokenisation, n-grams, Jaccard bounds)* | |

---

## 7. Frontend verification (outside pytest)

Automated and recorded, run against the production build served by `vite preview`:

| Check | Method | Result |
|---|---|---|
| Accessibility | axe-core, WCAG 2.0/2.1/2.2 A + AA, 6 pages × 2 viewports | **0 violations** |
| Horizontal overflow | 6 pages × 4 viewports (1440, 834, 390, 320 px) | **0 overflows** |
| Runtime errors | Console + page-error capture, same 24 combinations | **0 errors** |
| End-to-end journey | Real browser: file a report → receive hash → appear in queue → integrity chain | Passed |

The overflow check found and fixed three real defects (`minmax()` floors, a fieldset's
`min-inline-size`, and a file input's intrinsic width), and the accessibility check found and
fixed two (an unlabelled file input, and two sub-4.5:1 contrast pairs). Both classes of defect
were invisible to the build and the backend tests, which is why the browser check exists.
