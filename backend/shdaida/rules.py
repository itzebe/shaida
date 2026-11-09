"""Deterministic procedural verification of polling-unit result records.

Every check here is an *objective, publicly-stated arithmetic or consistency rule*.
Nothing in this module infers intent, and nothing here can accuse anyone.

The five rule families mirror the anomaly types the official synthetic pack injects
(`data/synthetic/DATA_DICTIONARY.md`), so results are directly comparable to a known
ground truth:

    accredited_exceeds_registered, sum_mismatch, digit_transposition,
    suspicious_round_numbers, duplicated_from_previous_unit

Two deliberate design decisions, both required by the official Track 2 brief:

* **Benign explanations are always offered.** A flag is a question for a human, so each
  finding carries plausible innocent causes (transcription error, damaged sheet, natural
  turnout variation) alongside the rule it violated.
* **Rules are tiered by strength.** A hard arithmetic contradiction (`accredited >
  registered`, `sum_mismatch`) is a *structural* finding. Statistical heuristics
  (`suspicious_round_numbers`, `digit_transposition`) are *advisory* only, because the
  brief warns that "natural variation flagged as fraud" and the base-rate fallacy are the
  classic failure modes. Advisory findings never carry the same weight as structural ones.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

# --------------------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ResultRecord:
    """One polling-unit result record (EC8A-shaped).

    ``votes`` maps candidate/party code -> votes. Party codes are abstract labels (A, B, C…)
    exactly as in the official synthetic pack; SHAIDA has no concept of a real party.
    """

    pu_id: str
    registered_voters: int
    accredited_voters: int
    votes: dict[str, int]
    rejected_votes: int

    @property
    def total_valid(self) -> int:
        return sum(self.votes.values())

    @property
    def total_cast(self) -> int:
        return self.total_valid + self.rejected_votes


@dataclass(frozen=True)
class Finding:
    rule: str
    tier: str  # "structural" | "advisory"
    severity: int  # 0..4
    message: str
    detail: dict[str, Any] = field(default_factory=dict)
    benign_explanations: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class RuleReport:
    pu_id: str
    findings: tuple[Finding, ...]
    checks_run: tuple[str, ...]

    @property
    def structural_count(self) -> int:
        return sum(1 for f in self.findings if f.tier == "structural")

    @property
    def advisory_count(self) -> int:
        return sum(1 for f in self.findings if f.tier == "advisory")

    @property
    def needs_review(self) -> bool:
        return bool(self.findings)


# --------------------------------------------------------------------------------------
# Rule families
# --------------------------------------------------------------------------------------

ALL_RULES: tuple[str, ...] = (
    "R1_accredited_exceeds_registered",
    "R2_sum_mismatch",
    "R3_digit_transposition",
    "R4_suspicious_round_numbers",
    "R5_duplicated_from_previous_unit",
    "R6_turnout_outlier",
    "R7_negative_or_impossible",
)


def _r1_accredited_exceeds_registered(rec: ResultRecord) -> Finding | None:
    if rec.accredited_voters <= rec.registered_voters:
        return None
    over = rec.accredited_voters - rec.registered_voters
    return Finding(
        rule="R1_accredited_exceeds_registered",
        tier="structural",
        severity=4,
        message=(
            f"Accredited voters ({rec.accredited_voters}) exceed registered voters "
            f"({rec.registered_voters}) by {over}. This contradicts the register and is a "
            f"structural inconsistency that a reviewer should resolve against the source sheet."
        ),
        detail={
            "registered_voters": rec.registered_voters,
            "accredited_voters": rec.accredited_voters,
            "excess": over,
        },
        benign_explanations=(
            "Transcription error when copying the accredited figure from the sheet",
            "The registered-voters figure was misread from a damaged or faint form",
            "Two polling units' figures were merged on one line by mistake",
        ),
        evidence_refs=("registered_voters", "accredited_voters"),
    )


def _r2_sum_mismatch(rec: ResultRecord) -> Finding | None:
    if rec.total_cast == rec.accredited_voters:
        return None
    diff = rec.total_cast - rec.accredited_voters
    return Finding(
        rule="R2_sum_mismatch",
        tier="structural",
        severity=3,
        message=(
            f"Valid votes ({rec.total_valid}) plus rejected ({rec.rejected_votes}) equal "
            f"{rec.total_cast}, which differs from accredited voters ({rec.accredited_voters}) "
            f"by {diff}. The sheet's own arithmetic does not close."
        ),
        detail={
            "total_valid": rec.total_valid,
            "rejected_votes": rec.rejected_votes,
            "total_cast": rec.total_cast,
            "accredited_voters": rec.accredited_voters,
            "difference": diff,
        },
        benign_explanations=(
            "A candidate's tally was mis-added by hand",
            "Rejected ballots were recorded in the wrong box",
            "A figure was copied from the wrong row during collation",
        ),
        evidence_refs=("votes", "rejected_votes", "accredited_voters"),
    )


def _is_adjacent_transposition(a: int, b: int) -> bool:
    """True if ``b`` can be produced from ``a`` by swapping exactly two adjacent digits.

    This is deliberately far more specific than "the digits are a permutation of each other".
    A permutation test alone fires on coincidences — with five candidate tallies there is a
    real chance two of them just happen to share digits — and the official brief warns that
    over-firing heuristics are the classic failure mode of this kind of tool. Requiring an
    actual adjacent swap (the typo signature this rule exists to catch) removes almost all of
    the coincidence, at the cost of missing non-adjacent swaps, which are much rarer.
    """
    sa, sb = str(a), str(b)
    if len(sa) != len(sb):
        return False
    diffs = [i for i, (x, y) in enumerate(zip(sa, sb)) if x != y]
    if len(diffs) != 2:
        return False
    i, j = diffs
    if j != i + 1:
        return False
    return sa[i] == sb[j] and sa[j] == sb[i]


def _r3_digit_transposition(rec: ResultRecord) -> Finding | None:
    """Advisory: two tallies differ by exactly one adjacent digit swap."""
    codes = sorted(rec.votes)
    for i, a in enumerate(codes):
        for b in codes[i + 1 :]:
            va, vb = rec.votes[a], rec.votes[b]
            if va < 100 or vb < 100 or va == vb:
                continue
            if _is_adjacent_transposition(va, vb):
                return Finding(
                    rule="R3_digit_transposition",
                    tier="advisory",
                    severity=1,
                    message=(
                        f"Tallies for {a} ({va}) and {b} ({vb}) differ by exactly one adjacent "
                        f"digit swap. Advisory only: this is a recognisable typo signature but "
                        f"can also occur by chance."
                    ),
                    detail={"a": a, "b": b, "votes_a": va, "votes_b": vb},
                    benign_explanations=(
                        "A single adjacent-digit typo while transcribing one tally",
                        "Coincidence: adjacent-digit pairs recur naturally in small numbers",
                    ),
                    evidence_refs=("votes",),
                )
    return None


def _r4_suspicious_round_numbers(rec: ResultRecord) -> Finding | None:
    """Advisory: many tallies land exactly on multiples of 50.

    The official brief warns explicitly that this heuristic produces false alarms, so it is
    advisory, capped at severity 1, and only raised when *several* tallies round.
    """
    roundish = [c for c, v in rec.votes.items() if v > 0 and v % 50 == 0]
    if len(roundish) < 3:
        return None
    return Finding(
        rule="R4_suspicious_round_numbers",
        tier="advisory",
        severity=1,
        message=(
            f"{len(roundish)} of {len(rec.votes)} candidate tallies are exact multiples of 50 "
            f"({', '.join(sorted(roundish))}). Advisory only: rounding is common when tallies "
            f"are read aloud or estimated, and this rule is known to over-fire."
        ),
        detail={"rounded_candidates": sorted(roundish), "total_candidates": len(rec.votes)},
        benign_explanations=(
            "Tallies were read aloud and rounded during recording",
            "Small polling units genuinely produce round numbers",
            "The rule is statistically weak by construction and is advisory only",
        ),
        evidence_refs=("votes",),
    )


def _r5_duplicated_from_previous_unit(
    rec: ResultRecord, previous: ResultRecord | None
) -> Finding | None:
    """Detect a record whose candidate tallies repeat the previous unit's exactly.

    Only the *tallies* must match. Two adjacent polling units can legitimately differ in how
    many voters were accredited, so requiring the accreditation figure to match too would
    miss the copying error this rule exists to catch. (Confirmed against the official pack:
    every row labelled ``duplicated_from_previous_unit`` repeats the previous row's votes
    while its accreditation figure differs.)
    """
    if previous is None or rec.pu_id == previous.pu_id:
        return None
    if not rec.votes or rec.votes != previous.votes:
        return None
    return Finding(
        rule="R5_duplicated_from_previous_unit",
        tier="structural",
        severity=3,
        message=(
            f"Every candidate tally here is identical to unit {previous.pu_id}, although the "
            f"accreditation figures differ. Identical tallies for two different units normally "
            f"mean a copying error, not two identical electorates."
        ),
        detail={"duplicate_of": previous.pu_id, "shared_votes": rec.votes},
        benign_explanations=(
            "The previous unit's sheet was photographed or uploaded twice",
            "A spreadsheet row was duplicated during data entry",
            "A collation officer copied the wrong row forward",
        ),
        evidence_refs=("votes",),
    )


def _r6_turnout_outlier(rec: ResultRecord, cohort_turnouts: Sequence[float]) -> Finding | None:
    """Advisory: accreditation share is a strong outlier for the cohort.

    Uses a robust median/MAD test rather than a mean/σ test, so a handful of extreme units
    cannot inflate the threshold and hide themselves. When the cohort is degenerate (every unit
    the same, so MAD is zero) the MAD test cannot be computed at all; rather than silently
    disabling the rule, we fall back to an absolute deviation threshold and say so in the detail.
    """
    if rec.registered_voters <= 0 or len(cohort_turnouts) < 20:
        return None
    share = rec.accredited_voters / rec.registered_voters
    median = _median(cohort_turnouts)
    mad = _median([abs(x - median) for x in cohort_turnouts])

    if mad > 0:
        z = 0.6745 * (share - median) / mad
        if z <= 6.0:
            return None
        statistic = {"robust_z": round(z, 2)}
        comparison = f"robust z ≈ {z:.1f}"
    else:
        # Degenerate cohort: fall back to a plain absolute deviation and disclose it.
        deviation = share - median
        if abs(deviation) < 0.4:
            return None
        statistic = {"absolute_deviation": round(deviation, 4), "fallback": "mad was zero"}
        comparison = f"deviation ≈ {deviation:+.1%}"

    return Finding(
        rule="R6_turnout_outlier",
        tier="advisory",
        severity=2,
        message=(
            f"Accreditation share here is {share:.1%} against a cohort median of {median:.1%} "
            f"({comparison}). Advisory only: turnout genuinely varies by settlement, security "
            f"and accessibility, and outliers are expected in any real distribution."
        ),
        detail={"share": round(share, 4), "median": round(median, 4), **statistic},
        benign_explanations=(
            "Urban units with high footfall genuinely reach higher turnout",
            "A neighbouring unit was merged into this one for the day",
            "Natural variation: some units are always outliers",
        ),
        evidence_refs=("accredited_voters", "registered_voters"),
    )


def _r7_negative_or_impossible(rec: ResultRecord) -> Finding | None:
    problems: list[str] = []
    if rec.registered_voters < 0:
        problems.append("registered_voters is negative")
    if rec.accredited_voters < 0:
        problems.append("accredited_voters is negative")
    if rec.rejected_votes < 0:
        problems.append("rejected_votes is negative")
    negatives = [c for c, v in rec.votes.items() if v < 0]
    if negatives:
        problems.append(f"negative tallies for {', '.join(sorted(negatives))}")
    if not problems:
        return None
    return Finding(
        rule="R7_negative_or_impossible",
        tier="structural",
        severity=4,
        message=(
            "The record contains a value that cannot occur on a real sheet: "
            + "; ".join(problems)
            + ". This is almost always a data-entry fault and must be corrected at source."
        ),
        detail={"problems": problems},
        benign_explanations=(
            "A minus sign was typed where a dash was intended",
            "A column was mis-aligned during data entry",
        ),
        evidence_refs=("votes", "registered_voters", "accredited_voters", "rejected_votes"),
    )


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------


def _median(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2.0


# --------------------------------------------------------------------------------------
# Public entry points
# --------------------------------------------------------------------------------------


def check_record(rec: ResultRecord, cohort_turnouts: Sequence[float] = ()) -> RuleReport:
    """Run every rule against a single record."""
    findings: list[Finding] = []
    for candidate in (
        _r7_negative_or_impossible(rec),
        _r1_accredited_exceeds_registered(rec),
        _r2_sum_mismatch(rec),
        _r3_digit_transposition(rec),
        _r4_suspicious_round_numbers(rec),
        _r6_turnout_outlier(rec, cohort_turnouts),
    ):
        if candidate is not None:
            findings.append(candidate)
    findings.sort(key=lambda f: (-f.severity, f.rule))
    return RuleReport(pu_id=rec.pu_id, findings=tuple(findings), checks_run=ALL_RULES)


def check_batch(records: Iterable[ResultRecord]) -> list[RuleReport]:
    """Run every rule across a batch, enabling cross-record rules.

    Cross-record rules (duplicate detection, cohort outliers) need the whole set, so the
    batch is materialised once, then each record is checked with its neighbour and the
    cohort's turnout distribution available.
    """
    materialised = list(records)
    turnouts = [
        r.accredited_voters / r.registered_voters
        for r in materialised
        if r.registered_voters > 0
    ]
    reports: list[RuleReport] = []
    previous: ResultRecord | None = None
    for rec in materialised:
        findings = list(check_record(rec, turnouts).findings)
        dup = _r5_duplicated_from_previous_unit(rec, previous)
        if dup is not None:
            findings.append(dup)
        findings.sort(key=lambda f: (-f.severity, f.rule))
        reports.append(RuleReport(pu_id=rec.pu_id, findings=tuple(findings), checks_run=ALL_RULES))
        previous = rec
    return reports


def implied_registered_floor(accredited: int, rejected: int, total_valid: int) -> int:
    """Smallest registered-voter count consistent with the recorded figures.

    Used by the API to give a reviewer a concrete number to check, rather than a vague
    complaint. Purely arithmetic; carries no judgement.
    """
    return max(0, int(math.ceil(max(accredited, rejected + total_valid))))


def arithmetic_certificate(rec: ResultRecord) -> dict[str, Any]:
    """A hand-checkable statement of every arithmetic identity the record must satisfy.

    The point of a certificate is that a reviewer can confirm it with a pen in a few seconds
    and without trusting any model. Each line states the equation, the two sides' values, and
    whether they balance. Nothing here is inferred; it is all arithmetic over the record's own
    fields.
    """
    lines: list[dict[str, Any]] = []

    lines.append(
        {
            "identity": "sum of candidate votes + rejected = total votes cast",
            "left": rec.total_valid + rec.rejected_votes,
            "right": rec.total_cast,
            "balances": rec.total_valid + rec.rejected_votes == rec.total_cast,
            "note": "Always true by definition; shown so the reviewer sees the totals used.",
        }
    )
    lines.append(
        {
            "identity": "total votes cast = accredited voters",
            "left": rec.total_cast,
            "right": rec.accredited_voters,
            "balances": rec.total_cast == rec.accredited_voters,
            "note": (
                "The sheet's own totals should close. A shortfall usually means the sheet's "
                "tallies are incomplete rather than that anything improper occurred."
            ),
        }
    )
    lines.append(
        {
            "identity": "accredited voters <= registered voters",
            "left": rec.accredited_voters,
            "right": rec.registered_voters,
            "balances": rec.accredited_voters <= rec.registered_voters,
            "note": "Accreditation cannot exceed the register at the same unit.",
        }
    )
    lines.append(
        {
            "identity": "every tally >= 0",
            "left": min(rec.votes.values()) if rec.votes else 0,
            "right": 0,
            "balances": all(v >= 0 for v in rec.votes.values()),
            "note": "A negative tally is a data-entry fault, not a result.",
        }
    )

    return {
        "pu_id": rec.pu_id,
        "figures": {
            "registered_voters": rec.registered_voters,
            "accredited_voters": rec.accredited_voters,
            "candidate_votes": dict(sorted(rec.votes.items())),
            "total_valid": rec.total_valid,
            "rejected_votes": rec.rejected_votes,
            "total_cast": rec.total_cast,
        },
        "lines": lines,
        "all_balance": all(line["balances"] for line in lines),
        "method": "arithmetic over the record's own fields; no inference, no model",
    }
