"""Shared vocabularies: incident categories, evidence kinds, and the language of *flags*.

Two rules are enforced here rather than left to callers:

1. **No fraud vocabulary.** ``assert_no_verdict_language`` is used by tests and by the API
   layer so that no output can describe a record as fraudulent, rigged or stolen. SHAIDA
   flags; humans decide.
2. **Severity is ordinal and bounded.** ``0..4`` matches the official synthetic incident
   pack so evaluation is directly comparable.
"""

from __future__ import annotations

from typing import Final

# Incident categories.
#
# The first seven are the **exact** strings used by the official synthetic incident pack
# (`incident_reports_synthetic.csv`), so SHAIDA's severity model trains and evaluates on the
# organisers' own vocabulary. The remainder are categories the official track briefs name
# explicitly (result-sheet handling, BVAS malfunction, upload delay, misinformation) and are
# needed for a real observer workflow.
INCIDENT_CATEGORIES: Final[tuple[str, ...]] = (
    # --- official pack vocabulary -------------------------------------------------
    "logistics_delay",
    "positive_practice",
    "intimidation",
    "accessibility_barrier",
    "information_gap",
    "equipment_failure",
    "queue_management",
    # --- additional categories named in the technical briefs ----------------------
    "result_sheet_issue",
    "result_upload_delay",
    "bvas_malfunction",
    "misinformation_claim",
    "voter_intimidation",
    "violence_or_threat",
    "staffing_shortfall",
    "procedural_irregularity",
    "other",
)

# Categories that can endanger a person. These change the *handling*, not the verdict:
# identity is stripped, location is coarsened further, and a reviewer is notified.
SENSITIVE_CATEGORIES: Final[frozenset[str]] = frozenset(
    {"intimidation", "voter_intimidation", "violence_or_threat"}
)

REPORTER_TYPES: Final[tuple[str, ...]] = (
    "citizen",
    "observer",
    "party_agent",
    "official",
    "simulated_agent",
)

EVIDENCE_KINDS: Final[tuple[str, ...]] = (
    "photo",
    "document_scan",
    "result_sheet",
    "audio",
    "video",
    "text_only",
    "c2pa_manifest",
)

SEVERITY_LABELS: Final[dict[int, str]] = {
    0: "informational",
    1: "minor",
    2: "moderate",
    3: "serious",
    4: "critical",
}

# Words that would amount to SHAIDA declaring a verdict. Their presence in any
# user-facing flag message is a bug, and is asserted against in the test suite.
FORBIDDEN_VERDICT_TERMS: Final[tuple[str, ...]] = (
    "fraud",
    "fraudulent",
    "rigged",
    "stolen",
    "fake",
    "manipulated",
    "cheated",
    "illegal result",
    "winner",
    "declared winner",
    "guilty",
    "corrupt",
    "falsified",
)


class VerdictLanguageError(ValueError):
    """Raised when generated text crosses the line from flagging into judging."""


def assert_no_verdict_language(*texts: str) -> None:
    """Raise if any supplied text contains forbidden verdict vocabulary."""
    for text in texts:
        lowered = (text or "").lower()
        for term in FORBIDDEN_VERDICT_TERMS:
            if term in lowered:
                raise VerdictLanguageError(
                    f"output contains verdict vocabulary {term!r}; SHAIDA flags, it does not judge"
                )
