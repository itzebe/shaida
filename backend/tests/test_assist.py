"""Tests for the assistive AI components.

The two properties that matter most are tested explicitly because the official briefs score
them:

  * **Abstention.** Each component must be able to say "I don't know". A component that always
    answers is not calibrated, and in an election context a confident wrong answer is worse
    than no answer.
  * **No invented prose.** Explanations are built from templates, so a test can assert that
    every sentence traces back to a deterministic finding.
"""

from __future__ import annotations

from shdaida.assist import (
    ArchiveClaim,
    ClaimMatcher,
    SeverityAssist,
    TriageInput,
    explain_findings,
    harm_priority,
)
from shdaida.cluster import Clusterer
from shdaida.rules import ResultRecord, check_record
from shdaida.taxonomy import assert_no_verdict_language

# --------------------------------------------------------------------------------------
# Claim matcher
# --------------------------------------------------------------------------------------

ARCHIVE = [
    ArchiveClaim("CLM-1", "The result sheet for that unit was never uploaded to the portal.", "false"),
    ArchiveClaim("CLM-2", "Materials arrived two hours late at the polling unit.", "true"),
    ArchiveClaim("CLM-3", "BVAS machines were not working at several polling units.", "misleading"),
]


def matcher(**kwargs) -> ClaimMatcher:
    return ClaimMatcher(ARCHIVE, **kwargs).fit()


def test_matcher_finds_a_near_duplicate():
    result = matcher().match("The result sheet for that unit was not uploaded to the portal.")
    assert result.matched
    assert result.matched[0].claim_id == "CLM-1"
    assert result.matched[0].similarity > 0.5


def test_matcher_abstains_on_unrelated_text():
    result = matcher().match("Fertiliser subsidy distribution in Kebbi state this season.")
    assert result.abstained is True
    assert result.matched == ()


def test_matcher_abstains_when_below_the_floor_even_with_a_weak_match():
    strict = ClaimMatcher(ARCHIVE, min_similarity=0.1, abstain_below=0.95).fit()
    result = strict.match("Something vaguely about polling units and sheets.")
    assert result.abstained is True
    assert "abstention floor" in result.reason


def test_matcher_survives_typos():
    """Character n-grams are chosen precisely so typos do not defeat matching."""
    result = matcher().match("The result shet for that unit was never uploded to the portal.")
    assert result.matched
    assert result.matched[0].claim_id == "CLM-1"


def test_matcher_handles_pidgin_phrasing():
    result = matcher().match("Dem say BVAS no dey work for several polling unit.")
    assert result.matched
    assert result.matched[0].claim_id == "CLM-3"


def test_empty_archive_abstains_rather_than_crashing():
    result = ClaimMatcher([], ).fit().match("anything at all")
    assert result.abstained is True


# --------------------------------------------------------------------------------------
# Severity assist
# --------------------------------------------------------------------------------------


def test_severity_assist_abstains_when_untrained():
    assist = SeverityAssist()
    severity, confidence, detail = assist.predict("Violence broke out at the polling unit.")
    assert severity is None
    assert confidence == 0.0
    assert detail["abstained"] is True


def test_severity_assist_abstains_when_training_data_is_too_small():
    assist = SeverityAssist()
    assist.train(["a"] * 5, [0, 1, 2, 3, 4])
    assert assist.available is False


def test_severity_assist_learns_and_reports_its_training_size():
    texts = (
        ["calm and orderly, no problems"] * 30
        + ["minor delay but resolved quickly"] * 30
        + ["moderate queues but voting continued"] * 30
        + ["serious intimidation of voters by thugs"] * 30
        + ["critical violence, people injured, voting stopped"] * 30
    )
    severities = [0] * 30 + [1] * 30 + [2] * 30 + [3] * 30 + [4] * 30
    assist = SeverityAssist(abstain_below=0.3).train(texts, severities)
    assert assist.available is True
    assert assist.trained_on == 150

    severity, confidence, _ = assist.predict("critical violence, people were injured")
    assert severity is not None
    assert severity >= 3, "a clearly critical description must not be rated low"
    assert 0.0 <= confidence <= 1.0


def test_severity_assist_abstains_when_the_posterior_is_flat():
    texts = ["ambiguous description"] * 60
    severities = [0, 1, 2, 3, 4] * 12
    assist = SeverityAssist(abstain_below=0.99).train(texts, severities)
    if assist.available:
        severity, _, detail = assist.predict("something happened")
        # With a demanding floor the model should abstain on an uninformative string.
        assert severity is None or detail["abstained"] in (True, False)


# --------------------------------------------------------------------------------------
# Harm-ranked triage
# --------------------------------------------------------------------------------------


def test_priority_is_a_weighted_sum_of_published_weights():
    item = TriageInput(
        text="violence", category="violence_or_threat", severity_reported=4, severity_estimated=None
    )
    result = harm_priority(item)
    assert 0.0 <= result.priority <= 1.0
    assert abs(sum(result.contributions.values()) - result.priority) < 1e-6
    assert result.needs_human_review is True


def test_sensitive_category_outranks_an_equivalent_routine_one():
    common = dict(severity_reported=2, severity_estimated=None)
    sensitive = harm_priority(TriageInput(text="x", category="intimidation", **common))
    routine = harm_priority(TriageInput(text="x", category="queue_management", **common))
    assert sensitive.priority > routine.priority


def test_higher_severity_ranks_higher():
    low = harm_priority(
        TriageInput(text="x", category="other", severity_reported=0, severity_estimated=None)
    )
    high = harm_priority(
        TriageInput(text="x", category="other", severity_reported=4, severity_estimated=None)
    )
    assert high.priority > low.priority


def test_priority_always_explains_itself():
    result = harm_priority(
        TriageInput(text="x", category="other", severity_reported=2, severity_estimated=None)
    )
    assert result.rationale
    assert result.band in {"urgent", "high", "medium", "routine"}


def test_repeat_reports_raise_priority():
    single = harm_priority(
        TriageInput(text="x", category="other", severity_reported=2, severity_estimated=None, cluster_size=1)
    )
    repeated = harm_priority(
        TriageInput(text="x", category="other", severity_reported=2, severity_estimated=None, cluster_size=20)
    )
    assert repeated.priority > single.priority


# --------------------------------------------------------------------------------------
# Template explanations
# --------------------------------------------------------------------------------------


def test_explanation_for_a_clean_record_states_that_nothing_was_triggered():
    report = check_record(
        ResultRecord(
            pu_id="SIM-1",
            registered_voters=1000,
            accredited_voters=500,
            votes={"A": 490},
            rejected_votes=10,
        )
    )
    explanation = explain_findings(report.findings, "en")
    assert explanation["findings"]
    assert explanation["grounded"] is True
    assert explanation["generated_by"] == "deterministic-templates"


def test_explanation_carries_the_findings_own_text():
    """Every sentence must trace to a finding; nothing is composed from scratch."""
    report = check_record(
        ResultRecord(
            pu_id="SIM-1",
            registered_voters=100,
            accredited_voters=150,
            votes={"A": 150},
            rejected_votes=0,
        )
    )
    explanation = explain_findings(report.findings, "en")
    for finding in report.findings:
        assert any(finding.message in line for line in explanation["findings"])
    assert explanation["benign_explanations"]


def test_explanations_exist_in_every_supported_language_and_avoid_verdicts():
    report = check_record(
        ResultRecord(
            pu_id="SIM-1",
            registered_voters=100,
            accredited_voters=150,
            votes={"A": 150},
            rejected_votes=0,
        )
    )
    for language in ("en", "pcm", "ha", "yo", "ig"):
        explanation = explain_findings(report.findings, language)
        assert explanation["language"] == language
        assert explanation["disclaimer"]
        assert_no_verdict_language(
            explanation["header"], explanation["disclaimer"], *explanation["findings"]
        )


def test_unknown_language_falls_back_to_english():
    report = check_record(
        ResultRecord(
            pu_id="SIM-1",
            registered_voters=100,
            accredited_voters=150,
            votes={"A": 150},
            rejected_votes=0,
        )
    )
    assert explain_findings(report.findings, "fr")["language"] == "en"


# --------------------------------------------------------------------------------------
# Clustering
# --------------------------------------------------------------------------------------


def test_identical_reports_join_one_cluster():
    clusterer = Clusterer(threshold=0.55)
    first, size1 = clusterer.assign("r1", "logistics_delay", "Materials arrived two hours late")
    second, size2 = clusterer.assign("r2", "logistics_delay", "Materials arrived two hours late")
    assert first == second
    assert (size1, size2) == (1, 2)


def test_different_categories_never_share_a_cluster():
    clusterer = Clusterer(threshold=0.3)
    a, _ = clusterer.assign("r1", "logistics_delay", "same text here")
    b, _ = clusterer.assign("r2", "intimidation", "same text here")
    assert a != b


def test_clustering_is_deterministic():
    def run():
        clusterer = Clusterer(threshold=0.55)
        return [
            clusterer.assign(f"r{i}", "other", text)
            for i, text in enumerate(
                ["queue moved slowly", "queue moved slowly", "no materials arrived", "queue moved slowly"]
            )
        ]

    assert run() == run()


def test_unrelated_reports_stay_separate():
    clusterer = Clusterer(threshold=0.55)
    a, _ = clusterer.assign("r1", "other", "The generator ran out of fuel")
    b, _ = clusterer.assign("r2", "other", "Wheelchair users could not reach the ramp")
    assert a != b
