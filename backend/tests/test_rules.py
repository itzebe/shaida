"""Tests for the deterministic rule engine.

The most important tests here are the *negative* ones: a clean record must produce no
findings, and each rule must be provably capable of staying silent. A rule engine that flags
everything is worse than useless in an election context.
"""

from __future__ import annotations

import pytest

from shdaida.rules import (
    ALL_RULES,
    ResultRecord,
    arithmetic_certificate,
    check_batch,
    check_record,
    implied_registered_floor,
)


def rec(**kwargs) -> ResultRecord:
    base = dict(
        pu_id="SIM-00001",
        registered_voters=1000,
        accredited_voters=500,
        votes={"A": 200, "B": 150, "C": 140},
        rejected_votes=10,
    )
    base.update(kwargs)
    return ResultRecord(**base)


# --------------------------------------------------------------------------------------
# Clean records must stay clean
# --------------------------------------------------------------------------------------


def test_clean_record_produces_no_findings():
    report = check_record(rec())
    assert report.findings == ()
    assert report.needs_review is False
    assert report.structural_count == 0


def test_clean_record_checks_every_rule():
    report = check_record(rec())
    assert set(report.checks_run) == set(ALL_RULES)


# --------------------------------------------------------------------------------------
# R1 — accredited exceeds registered
# --------------------------------------------------------------------------------------


def test_r1_fires_and_is_structural():
    report = check_record(rec(registered_voters=100, accredited_voters=150, votes={"A": 150}))
    rules = {f.rule for f in report.findings}
    assert "R1_accredited_exceeds_registered" in rules
    finding = next(f for f in report.findings if f.rule == "R1_accredited_exceeds_registered")
    assert finding.tier == "structural"
    assert finding.severity == 4
    assert finding.benign_explanations, "every flag must offer innocent explanations"


def test_r1_does_not_fire_when_equal():
    report = check_record(rec(registered_voters=500, accredited_voters=500, votes={"A": 490}, rejected_votes=10))
    assert "R1_accredited_exceeds_registered" not in {f.rule for f in report.findings}


# --------------------------------------------------------------------------------------
# R2 — the sheet's own arithmetic
# --------------------------------------------------------------------------------------


def test_r2_fires_when_totals_do_not_close():
    report = check_record(rec(votes={"A": 10, "B": 10}, rejected_votes=5, accredited_voters=500))
    assert "R2_sum_mismatch" in {f.rule for f in report.findings}


def test_r2_silent_when_totals_close():
    report = check_record(rec(votes={"A": 100}, rejected_votes=0, accredited_voters=100))
    assert "R2_sum_mismatch" not in {f.rule for f in report.findings}


# --------------------------------------------------------------------------------------
# R3 — adjacent digit transposition (advisory, and deliberately narrow)
# --------------------------------------------------------------------------------------


def test_r3_fires_on_adjacent_swap():
    report = check_record(rec(votes={"A": 1234, "B": 1243, "C": 500}))
    assert "R3_digit_transposition" in {f.rule for f in report.findings}


def test_r3_is_advisory_only():
    report = check_record(rec(votes={"A": 1234, "B": 1243, "C": 500}))
    finding = next(f for f in report.findings if f.rule == "R3_digit_transposition")
    assert finding.tier == "advisory"
    assert finding.severity <= 1


def test_r3_silent_on_non_adjacent_permutation():
    """1342 and 1243 share digits but are not an adjacent swap: the rule must stay quiet."""
    report = check_record(rec(votes={"A": 1342, "B": 1243, "C": 500}))
    assert "R3_digit_transposition" not in {f.rule for f in report.findings}


def test_r3_silent_on_identical_values():
    report = check_record(rec(votes={"A": 300, "B": 300, "C": 500}))
    assert "R3_digit_transposition" not in {f.rule for f in report.findings}


# --------------------------------------------------------------------------------------
# R4 — round numbers (advisory, capped)
# --------------------------------------------------------------------------------------


def test_r4_fires_on_three_round_tallies():
    report = check_record(rec(votes={"A": 200, "B": 150, "C": 300, "D": 47}))
    assert "R4_suspicious_round_numbers" in {f.rule for f in report.findings}


def test_r4_silent_on_two_round_tallies():
    report = check_record(rec(votes={"A": 200, "B": 150, "C": 47, "D": 63}))
    assert "R4_suspicious_round_numbers" not in {f.rule for f in report.findings}


# --------------------------------------------------------------------------------------
# R5 — duplicated tallies from the previous unit
# --------------------------------------------------------------------------------------


def test_r5_fires_when_tallies_repeat_the_previous_unit():
    first = rec(pu_id="SIM-00001", votes={"A": 104, "B": 20}, accredited_voters=431)
    second = rec(pu_id="SIM-00002", votes={"A": 104, "B": 20}, accredited_voters=847)
    reports = check_batch([first, second])
    assert "R5_duplicated_from_previous_unit" in {f.rule for f in reports[1].findings}


def test_r5_silent_when_tallies_differ():
    first = rec(pu_id="SIM-00001", votes={"A": 104, "B": 20})
    second = rec(pu_id="SIM-00002", votes={"A": 105, "B": 20})
    reports = check_batch([first, second])
    assert "R5_duplicated_from_previous_unit" not in {f.rule for f in reports[1].findings}


def test_r5_does_not_fire_on_the_first_record():
    reports = check_batch([rec()])
    assert reports[0].findings == ()


# --------------------------------------------------------------------------------------
# R6 — cohort turnout outlier (needs a cohort, uses a robust statistic)
# --------------------------------------------------------------------------------------


def test_r6_silent_without_a_cohort():
    report = check_record(rec(registered_voters=1000, accredited_voters=1000, votes={"A": 990}, rejected_votes=10))
    assert "R6_turnout_outlier" not in {f.rule for f in report.findings}


def test_r6_fires_on_an_extreme_outlier_in_a_large_cohort():
    """A cohort with genuine variation, plus one unit far outside it."""
    cohort = [
        ResultRecord(
            pu_id=f"SIM-{i:05d}",
            registered_voters=1000,
            # Vary turnout so MAD is non-zero: 0.28 .. 0.42
            accredited_voters=280 + (i % 15) * 10,
            votes={"A": 200},
            rejected_votes=10,
        )
        for i in range(60)
    ]
    outlier = ResultRecord(
        pu_id="SIM-99999",
        registered_voters=1000,
        accredited_voters=1000,
        votes={"A": 990},
        rejected_votes=10,
    )
    reports = check_batch([*cohort, outlier])
    assert "R6_turnout_outlier" in {f.rule for f in reports[-1].findings}


def test_r6_falls_back_when_the_cohort_is_degenerate():
    """With zero variation the MAD test is undefined; the rule must still be able to fire."""
    cohort = [
        ResultRecord(
            pu_id=f"SIM-{i:05d}",
            registered_voters=1000,
            accredited_voters=300,
            votes={"A": 200},
            rejected_votes=10,
        )
        for i in range(40)
    ]
    outlier = ResultRecord(
        pu_id="SIM-99999",
        registered_voters=1000,
        accredited_voters=1000,
        votes={"A": 990},
        rejected_votes=10,
    )
    reports = check_batch([*cohort, outlier])
    finding = next(
        (f for f in reports[-1].findings if f.rule == "R6_turnout_outlier"), None
    )
    assert finding is not None
    assert finding.detail.get("fallback") == "mad was zero"


# --------------------------------------------------------------------------------------
# R7 — impossible values
# --------------------------------------------------------------------------------------


def test_r7_fires_on_negative_tally():
    report = check_record(rec(votes={"A": -5, "B": 100}, accredited_voters=95, rejected_votes=0))
    assert "R7_negative_or_impossible" in {f.rule for f in report.findings}


def test_r7_fires_on_negative_registered():
    report = check_record(rec(registered_voters=-1))
    assert "R7_negative_or_impossible" in {f.rule for f in report.findings}


# --------------------------------------------------------------------------------------
# Ordering, certificates, helpers
# --------------------------------------------------------------------------------------


def test_findings_are_ordered_structural_first():
    report = check_record(
        rec(registered_voters=100, accredited_voters=150, votes={"A": 200, "B": 150, "C": 300})
    )
    tiers = [f.tier for f in report.findings]
    assert tiers == sorted(tiers, key=lambda t: 0 if t == "structural" else 1)


def test_certificate_balances_for_a_clean_record():
    cert = arithmetic_certificate(rec(votes={"A": 400}, rejected_votes=100, accredited_voters=500))
    assert cert["all_balance"] is True
    assert all(line["balances"] for line in cert["lines"])


def test_certificate_flags_a_broken_record():
    cert = arithmetic_certificate(rec(votes={"A": 10}, rejected_votes=0, accredited_voters=500))
    assert cert["all_balance"] is False


def test_implied_registered_floor_is_the_maximum_constraint():
    assert implied_registered_floor(accredited=500, rejected=10, total_valid=400) == 500
    assert implied_registered_floor(accredited=100, rejected=10, total_valid=400) == 410


def test_no_finding_uses_verdict_language():
    """Every rule message must be a flag, never a judgement."""
    from shdaida.taxonomy import assert_no_verdict_language

    samples = [
        rec(registered_voters=100, accredited_voters=150, votes={"A": 150}),
        rec(votes={"A": 10}, rejected_votes=0, accredited_voters=500),
        rec(votes={"A": 1234, "B": 1243, "C": 500}),
        rec(votes={"A": 200, "B": 150, "C": 300, "D": 47}),
        rec(votes={"A": -5, "B": 100}),
    ]
    for sample in samples:
        for finding in check_record(sample).findings:
            assert_no_verdict_language(finding.message, *finding.benign_explanations)
