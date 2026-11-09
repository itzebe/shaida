"""Assistive AI: claim matching, severity estimation, harm-ranked triage, explanations.

Four deliberately narrow components. Each one is bounded, inspectable, and able to
**abstain**, because the official briefs score calibration and abstention explicitly and
forbid the two failure modes that make election AI dangerous: confident wrong answers, and
machinery that quietly decides things a human should decide.

1. ``ClaimMatcher`` — TF-IDF character n-gram retrieval with cosine similarity, over a
   fact-check archive. Answers "have we already checked something like this?", never
   "is this true?". Multilingual via :mod:`shdaida.text`. Abstains below a similarity floor.

2. ``SeverityAssist`` — multinomial logistic regression over text features, trained locally
   on the official synthetic incident pack. Estimates *reported* severity to help order a
   queue. Abstains when the posterior is flat. It never sees a reporter's identity.

3. ``harm_priority`` — a transparent, published weighted model that ranks a report for human
   attention. It combines the severity assist with reach, sensitivity and evidence signals.
   Every weight is documented and every contribution is returned, so a reviewer can see why
   something is at the top of the queue.

4. ``explain_findings`` — template-grounded natural-language explanations.

   **Design decision (deliberate):** explanations are generated from *templates filled with
   deterministic findings*, not by a language model. A generative model phrasing a claim
   about a citizen's evidence could invent a fact, and the official Track 3 brief sets a
   zero-unsupported-answers target. Templates make "no unsupported statement" structurally
   true rather than merely tested for. This is the responsible-AI choice, and it is why
   SHAIDA's AI budget is spent on retrieval and ranking rather than on prose.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from . import text as T
from .taxonomy import SENSITIVE_CATEGORIES, SEVERITY_LABELS, assert_no_verdict_language

# --------------------------------------------------------------------------------------
# 1. Claim matching
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ArchiveClaim:
    claim_id: str
    text: str
    label: str  # true | false | misleading | unverifiable
    language: str = "en"
    channel: str = "unknown"
    verdict_summary: str = ""


@dataclass(frozen=True)
class ClaimMatch:
    claim_id: str
    similarity: float
    label: str
    language: str
    channel: str
    verdict_summary: str


@dataclass(frozen=True)
class MatchResult:
    matched: tuple[ClaimMatch, ...]
    abstained: bool
    reason: str
    top_similarity: float


class ClaimMatcher:
    """Character n-gram TF-IDF retrieval over a fact-check archive.

    Implemented with scikit-learn's ``TfidfVectorizer`` using ``analyzer="char_wb"`` with a
    3–5 gram range. Character n-grams are the right choice here because the official Track 1
    success criteria include robustness to typos, paraphrase and code-switching, all of
    which break word-level matching. No embeddings model is downloaded, so the component
    works fully offline with no API key.
    """

    def __init__(
        self,
        claims: Sequence[ArchiveClaim],
        min_similarity: float = 0.35,
        abstain_below: float = 0.45,
    ) -> None:
        self.claims = list(claims)
        self.min_similarity = min_similarity
        self.abstain_below = abstain_below
        self._vectorizer = None
        self._matrix = None
        self._fitted = False

    def fit(self) -> "ClaimMatcher":
        from sklearn.feature_extraction.text import TfidfVectorizer

        if not self.claims:
            self._fitted = True
            return self
        corpus = [T.normalise(c.text) for c in self.claims]
        self._vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=1,
            sublinear_tf=True,
        )
        self._matrix = self._vectorizer.fit_transform(corpus)
        self._fitted = True
        return self

    def match(self, query: str, top_k: int = 5) -> MatchResult:
        if not self._fitted:
            self.fit()
        if not self.claims or self._vectorizer is None or self._matrix is None:
            return MatchResult((), True, "archive is empty", 0.0)

        from sklearn.metrics.pairwise import cosine_similarity

        qvec = self._vectorizer.transform([T.normalise(query)])
        sims = cosine_similarity(qvec, self._matrix)[0]
        order = sims.argsort()[::-1]
        top = float(sims[order[0]]) if len(order) else 0.0

        matches: list[ClaimMatch] = []
        for idx in order[:top_k]:
            score = float(sims[idx])
            if score < self.min_similarity:
                break
            claim = self.claims[int(idx)]
            matches.append(
                ClaimMatch(
                    claim_id=claim.claim_id,
                    similarity=round(score, 4),
                    label=claim.label,
                    language=claim.language,
                    channel=claim.channel,
                    verdict_summary=claim.verdict_summary,
                )
            )

        if not matches:
            return MatchResult(
                (),
                True,
                "no archived claim is similar enough; treat this as new and route to a human",
                top,
            )
        if top < self.abstain_below:
            return MatchResult(
                tuple(matches),
                True,
                (
                    f"closest archive match is only {top:.2f} similar, below the "
                    f"{self.abstain_below:.2f} abstention floor; a human must decide whether it "
                    f"really is the same claim"
                ),
                top,
            )
        return MatchResult(
            tuple(matches),
            False,
            f"closest archive match is {top:.2f} similar",
            top,
        )


# --------------------------------------------------------------------------------------
# 2. Severity assist
# --------------------------------------------------------------------------------------

# Category cues used as features. Multi-lingual, including Pidgin and the major Nigerian
# languages, because the official pack mixes them.
_SEVERITY_CUES: dict[str, tuple[str, ...]] = {
    "violence": (
        "violence", "fight", "attack", "gun", "shoot", "machete", "thug", "beaten",
        "killed", "injury", "wounded", "stabbing", "bomb", "threat", "threaten",
        "danger", "unsafe", "hoodlums", "cultist", "violence", "yaƙi", "iwa",
    ),
    "intimidation": (
        "intimidat", "harass", "bribe", "bribery", "coerc", "pressure", "buying votes",
        "vote buying", "bought", "collect money", "witness", "refuse", "barred",
    ),
    "obstruction": (
        "blocked", "refused", "denied", "prevented", "turned away", "not allowed",
        "stopped", "hindered", "disallowed",
    ),
    "malfunction": (
        "malfunction", "not working", "faulty", "broken", "no network", "battery",
        "died", "failure", "error", "freeze", "hang", "device", "bvas", "unable",
    ),
    "logistics": (
        "late", "delay", "arrived", "no materials", "missing", "incomplete", "not arrived",
        "shortage", "ran out", "queue", "wait", "hours", "crowd",
    ),
    "accessibility": (
        "wheelchair", "ramp", "blind", "deaf", "disabled", "disability", "cannot reach",
        "no access", "step", "far", "distance", "elderly",
    ),
    "documentation": (
        "result sheet", "ec8a", "form", "tally", "upload", "irev", "scan", "photo",
        "record", "figure", "number", "mismatch", "not signed",
    ),
}

# Lexicons that shift reported severity, independent of category.
_SEVERITY_MODIFIERS: dict[str, tuple[str, ...]] = {
    "escalators": (
        "urgent", "immediately", "critical", "emergency", "severe", "serious",
        "widespread", "many people", "everyone", "nobody", "cannot vote", "refused all",
        "no voting", "shut down", "abandoned",
    ),
    "de-escalators": (
        "minor", "small", "few", "slight", "resolved", "fixed", "okay now", "later",
        "slightly", "one person", "a bit",
    ),
}

_NEGATION: re.Pattern[str] = re.compile(r"\b(not|no|never|without|isn't|wasn't|didn't)\b")


def _severity_features(raw_text: str) -> list[float]:
    """Transparent feature vector for the severity assist."""
    norm = T.normalise(raw_text)
    tokens = norm.split()
    n_tokens = max(1, len(tokens))
    features: list[float] = []

    for _name, cues in _SEVERITY_CUES.items():
        hits = sum(1 for cue in cues if cue in norm)
        features.append(hits / n_tokens * 100.0)

    for _name, cues in _SEVERITY_MODIFIERS.items():
        hits = sum(1 for cue in cues if cue in norm)
        features.append(hits / n_tokens * 100.0)

    # Length and negation are informative about how much detail a reporter gave.
    features.append(min(1.0, n_tokens / 60.0))
    features.append(len(_NEGATION.findall(norm)) / n_tokens * 100.0)
    return features


class SeverityAssist:
    """Multinomial logistic regression estimating *reported* severity (0–4).

    Trained locally on the official synthetic incident pack. If training data is absent or
    too small, the component disables itself and abstains rather than guessing — a missing
    model must never silently degrade into an unvalidated heuristic.
    """

    def __init__(self, abstain_below: float = 0.55) -> None:
        self.abstain_below = abstain_below
        self._model = None
        self._classes: list[int] = []
        self.trained_on: int = 0
        self.train_accuracy: float | None = None

    @property
    def available(self) -> bool:
        return self._model is not None

    def train(self, texts: Sequence[str], severities: Sequence[int]) -> "SeverityAssist":
        from sklearn.linear_model import LogisticRegression

        if len(texts) < 40 or len(set(severities)) < 2:
            self._model = None
            return self

        X = [_severity_features(t) for t in texts]
        y = list(severities)
        model = LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced")
        model.fit(X, y)
        self._model = model
        self._classes = [int(c) for c in model.classes_]
        self.trained_on = len(texts)
        self.train_accuracy = float(model.score(X, y))
        return self

    def predict(self, raw_text: str) -> tuple[int | None, float, dict[str, Any]]:
        """Return ``(severity_or_None, confidence, detail)``.

        ``None`` means abstention: the caller must not treat it as a severity of zero.
        """
        if self._model is None:
            return None, 0.0, {"abstained": True, "reason": "severity assist is not trained"}
        import numpy as np

        proba = self._model.predict_proba([_severity_features(raw_text)])[0]
        best = int(np.argmax(proba))
        confidence = float(proba[best])
        severity = self._classes[best]
        detail = {
            "abstained": confidence < self.abstain_below,
            "posterior": {str(c): round(float(p), 4) for c, p in zip(self._classes, proba)},
            "label": SEVERITY_LABELS.get(severity, "unknown"),
        }
        if confidence < self.abstain_below:
            return None, confidence, detail
        return severity, confidence, detail


# --------------------------------------------------------------------------------------
# 3. Harm-ranked triage
# --------------------------------------------------------------------------------------

# Published weights. Sum to 1.0 so the score is interpretable as a 0–1 priority.
HARM_WEIGHTS: dict[str, float] = {
    "severity": 0.35,
    "sensitivity": 0.20,
    "reach": 0.20,
    "evidence": 0.10,
    "procedural": 0.10,
    "freshness": 0.05,
}


@dataclass(frozen=True)
class TriageInput:
    text: str
    category: str
    severity_reported: int | None
    severity_estimated: int | None
    spread_score: float = 0.0  # 0..100, e.g. from a claim's reach signal
    has_evidence: bool = False
    mentions_procedure: bool = False
    age_hours: float = 0.0
    cluster_size: int = 1


@dataclass(frozen=True)
class TriageResult:
    priority: float
    band: str
    contributions: dict[str, float] = field(default_factory=dict)
    rationale: tuple[str, ...] = ()
    needs_human_review: bool = True


def _band(priority: float) -> str:
    if priority >= 0.75:
        return "urgent"
    if priority >= 0.55:
        return "high"
    if priority >= 0.35:
        return "medium"
    return "routine"


def harm_priority(item: TriageInput) -> TriageResult:
    """Rank a report for human attention. Explainable and fully reproducible.

    The score is a weighted sum of normalised, individually-reported signals. It is a
    *queue ordering*, never a judgement about the report's truth. The function always sets
    ``needs_human_review`` because a human must adjudicate every item.
    """
    severity = item.severity_reported
    if severity is None:
        severity = item.severity_estimated
    if severity is None:
        severity = 1  # neutral prior when both reporter and assist abstain
    sev_norm = min(1.0, max(0.0, severity / 4.0))

    sensitivity = 1.0 if item.category in SENSITIVE_CATEGORIES else 0.0
    reach = min(1.0, max(0.0, item.spread_score / 100.0))
    evidence = 1.0 if item.has_evidence else 0.25
    procedural = 1.0 if item.mentions_procedure else 0.0
    freshness = math.exp(-item.age_hours / 72.0) if item.age_hours > 0 else 1.0
    # Duplicate clusters matter: the same report arriving many times is a signal of scale.
    cluster = min(1.0, math.log1p(max(0, item.cluster_size - 1)) / math.log1p(20))

    parts = {
        "severity": sev_norm * HARM_WEIGHTS["severity"],
        "sensitivity": sensitivity * HARM_WEIGHTS["sensitivity"],
        "reach": max(reach, cluster * 0.8) * HARM_WEIGHTS["reach"],
        "evidence": evidence * HARM_WEIGHTS["evidence"],
        "procedural": procedural * HARM_WEIGHTS["procedural"],
        "freshness": freshness * HARM_WEIGHTS["freshness"],
    }
    priority = round(sum(parts.values()), 4)

    rationale: list[str] = []
    if sev_norm >= 0.75:
        rationale.append("reported or estimated severity is high")
    if sensitivity:
        rationale.append("category can endanger a person, so it is handled with extra privacy")
    if reach >= 0.5 or cluster >= 0.5:
        rationale.append("the same report is spreading or repeating, which raises its scale")
    if evidence:
        rationale.append("an evidence file was attached")
    if procedural:
        rationale.append("the report touches a published procedural rule")
    if not rationale:
        rationale.append("no strong signal; kept for completeness of the record")

    return TriageResult(
        priority=priority,
        band=_band(priority),
        contributions={k: round(v, 4) for k, v in parts.items()},
        rationale=tuple(rationale),
        needs_human_review=True,
    )


# --------------------------------------------------------------------------------------
# 4. Template-grounded explanations
# --------------------------------------------------------------------------------------

_EXPLANATION_TEMPLATES: dict[str, dict[str, str]] = {
    "en": {
        "header": "Why this record was flagged for review",
        "benign": "Plausible innocent explanations to rule out first",
        "ask": "What a reviewer should check next",
        "none": "No rule was triggered. The record is internally consistent under the checks SHAIDA runs.",
        "disclaimer": (
            "This is an automated flag based on arithmetic and consistency rules, not a finding "
            "about any person or about the outcome. Only a human reviewer can decide what it means."
        ),
    },
    "pcm": {
        "header": "Why we mark this record for person to check",
        "benign": "Normal things wey fit cause am, check dem first",
        "ask": "Wetin the reviewer suppose check next",
        "none": "No rule catch anything. The record balance well under the checks we dey run.",
        "disclaimer": (
            "Na machine flag based on arithmetic and consistency rules, no be judgement about "
            "anybody or about result. Only person fit decide wetin e mean."
        ),
    },
    "ha": {
        "header": "Dalilin da aka sa wannan rikodin a duba",
        "benign": "Abubuwan da ba laifi ba da za a fara dubawa",
        "ask": "Abin da mai dubawa zai duba na gaba",
        "none": "Babu wata doka da ta tashi. Rikodin ya daidaita a gwaje-gwajen da SHAIDA ke yi.",
        "disclaimer": (
            "Wannan tuta ce ta na'ura bisa ka'idojin lissafi da daidaito, ba hukunci ba ne kan "
            "kowa ko kan sakamako. Mutum ne kaɗai zai iya yanke shawara."
        ),
    },
    "yo": {
        "header": "Ìdí tí a fi sami àkọsílẹ̀ yìí fún àyẹ̀wò",
        "benign": "Àwọn ìdí tí kì í ṣe ẹ̀sùn tí ó yẹ kí a kọ́kọ́ yẹ̀wò",
        "ask": "Ohun tí olùyẹ̀wò yẹ kí ó yẹ̀wò tẹ̀le",
        "none": "Kò sí òfin tí ó dá. Àkọsílẹ̀ náà bá ara rẹ̀ mu ní ìbámu pẹ̀lú àwọn àyẹ̀wò SHAIDA.",
        "disclaimer": (
            "Àmì ẹ̀rọ ni èyí lórí àwọn òfin ìṣirò àti ìbámu, kì í ṣe ìdájọ́ lórí ẹnikẹ́ni tàbí "
            "èsì. Ènìyàn nìkan ló lè pinnu ìtumọ̀ rẹ̀."
        ),
    },
    "ig": {
        "header": "Ihe mere e ji akara ndekọ a maka nyocha",
        "benign": "Ihe ndị na-abụghị mmejọ kwesịrị ileba anya na mbụ",
        "ask": "Ihe onye nyocha kwesịrị ilele ọzọ",
        "none": "Ọ nweghị iwu dakwasịrị. Ndekọ a kwekọrọ n'okpuru nyocha SHAIDA na-eme.",
        "disclaimer": (
            "Nke a bụ akara igwe dabere na iwu mgbakọ na ndakọ, ọ bụghị mkpebi gbasara onye ọ "
            "bụla ma ọ bụ gbasara nsonaazụ. Naanị mmadụ nwere ike ikpebi ihe ọ pụtara."
        ),
    },
}

SUPPORTED_LANGUAGES: tuple[str, ...] = tuple(_EXPLANATION_TEMPLATES)


def explain_findings(findings: Iterable[Any], language: str = "en") -> dict[str, Any]:
    """Produce a grounded explanation of a rule report.

    ``findings`` are :class:`shdaida.rules.Finding` objects. The output is assembled from
    the finding's own ``message``, ``benign_explanations`` and ``evidence_refs``; no sentence
    is composed by a language model. ``assert_no_verdict_language`` is applied to the whole
    result as a hard guarantee.
    """
    lang = language if language in _EXPLANATION_TEMPLATES else "en"
    tpl = _EXPLANATION_TEMPLATES[lang]

    items = list(findings)
    lines: list[str] = []
    benign: list[str] = []
    asks: list[str] = []

    if not items:
        lines.append(tpl["none"])
    else:
        for finding in items:
            tier = getattr(finding, "tier", "advisory")
            marker = "structural" if tier == "structural" else "advisory"
            lines.append(f"[{marker}] {finding.message}")
            benign.extend(getattr(finding, "benign_explanations", ()) or ())
            refs = ", ".join(getattr(finding, "evidence_refs", ()) or ())
            if refs:
                asks.append(f"{finding.rule}: confirm against {refs} on the source sheet")

    # De-duplicate while preserving order.
    def _dedupe(values: Sequence[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                out.append(value)
        return out

    result = {
        "language": lang,
        "header": tpl["header"],
        "findings": lines,
        "benign_explanations": _dedupe(benign),
        "reviewer_next_steps": _dedupe(asks),
        "disclaimer": tpl["disclaimer"],
        "generated_by": "deterministic-templates",
        "grounded": True,
    }
    assert_no_verdict_language(
        result["header"],
        result["disclaimer"],
        *result["findings"],
        *result["benign_explanations"],
        *result["reviewer_next_steps"],
    )
    return result
