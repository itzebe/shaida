"""Evaluation regression guards.

These tests run the real evaluation against the official synthetic pack and assert that the
measured quality does not silently regress. They exist because the most likely future mistake
in this codebase is reintroducing a heuristic that looks clever and over-fires — which we
already did once (see ``REJECTED_HEURISTICS`` in the evaluation harness).

The thresholds are the measured values with a small margin, not aspirational targets. If a
change makes the engine worse, this fails and says by how much.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evaluation.evaluate import (  # noqa: E402
    DATA,
    evaluate_rules,
    measure_rejected_heuristics,
)
from shdaida.datasets import load_results  # noqa: E402

pytestmark = pytest.mark.skipif(
    not (DATA / "results_synthetic.csv").exists(),
    reason="official synthetic pack not present",
)


@pytest.fixture(scope="module")
def rules() -> dict:
    return evaluate_rules()


def test_recall_stays_high(rules):
    """Missing a labelled anomaly is the worst failure mode, so recall is the tightest bar."""
    assert rules["overall"]["recall"] >= 0.95, (
        f"recall dropped to {rules['overall']['recall']}; the engine is missing labelled anomalies"
    )


def test_clean_false_alarm_rate_stays_low(rules):
    """Flagging clean records destroys reviewer trust faster than anything else."""
    assert rules["clean_false_alarm_rate"] <= 0.02, (
        f"{rules['clean_false_alarm_rate']} of clean records were flagged"
    )


def test_flag_rate_stays_reviewable(rules):
    """If the engine flags a large share of records, the queue is useless to a human."""
    assert rules["flag_rate"] <= 0.10, (
        f"flag rate is {rules['flag_rate']}; a reviewer cannot act on that volume"
    )


def test_structural_findings_are_substantiated(rules):
    """Every structural finding must state a contradiction that actually holds."""
    assert rules["structural_substantiation"]["rate"] == 1.0


def test_structural_precision_is_perfect_on_labelled_rules(rules):
    for rule in (
        "R1_accredited_exceeds_registered",
        "R4_suspicious_round_numbers",
        "R5_duplicated_from_previous_unit",
    ):
        assert rules["per_rule"][rule]["precision"] == 1.0, f"{rule} produced a false alarm"
        assert rules["per_rule"][rule]["recall"] == 1.0, f"{rule} missed a labelled anomaly"


def test_rejected_heuristic_is_still_measured_and_still_bad():
    """The rejected heuristic must stay rejected, and the harness must keep proving it."""
    measurement = measure_rejected_heuristics(load_results(DATA / "results_synthetic.csv"))
    entry = measurement["single_digit_difference"]
    assert entry["status"] == "rejected"
    assert entry["fire_rate"] > 0.4, (
        "if this heuristic ever stops over-firing, revisit the decision to reject it"
    )


def test_adjacent_swap_rule_does_not_degrade_into_a_broad_permutation_test(rules):
    """R3 must stay narrow. A broad digit-permutation rule would fire on ~half the pack."""
    assert rules["per_rule"]["R3_digit_transposition"]["precision"] >= 0.0
    # The narrow rule fires on only a handful of records; a broad one fired on 444.
    fired = rules["per_rule"]["R3_digit_transposition"]["tp"] + rules["per_rule"][
        "R3_digit_transposition"
    ]["fp"]
    assert fired <= 20, f"R3 fired on {fired} records; it has become a broad heuristic again"


def test_processing_throughput_is_adequate(rules):
    """A reviewer-facing batch check must not be slow. 900 records is the pack size."""
    assert rules["records_per_second"] and rules["records_per_second"] > 500
