"""Service layer: the application's business logic, independent of HTTP.

Everything a reviewer-facing product must do lives here so it can be unit-tested without a
web server: create a report, triage it, cluster it, hash it, review it, verify it, run the
result rules, match a claim, and aggregate with k-anonymity.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

from .assist import (
    SUPPORTED_LANGUAGES,
    ClaimMatcher,
    SeverityAssist,
    TriageInput,
    explain_findings,
    harm_priority,
)
from .cluster import Clusterer
from .config import Settings, load_settings
from .datasets import (
    load_anomaly_labels,
    load_claims,
    load_incidents,
    load_polling_units,
    load_results,
)
from .provenance import content_hash
from .rules import ResultRecord, RuleReport, check_batch, check_record
from .storage import Store, new_id
from .taxonomy import (
    EVIDENCE_KINDS,
    INCIDENT_CATEGORIES,
    REPORTER_TYPES,
    SENSITIVE_CATEGORIES,
)

_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
_PROCEDURAL_CUES = re.compile(
    r"\b(ec8a|ec8|result sheet|form|tally|upload|irev|collation|accredit|"
    r"registered voters|rejected|ballot|bvas|presiding officer)\b",
    re.IGNORECASE,
)

DECISIONS = ("accepted", "needs_more_evidence", "referred_to_cso", "not_pursued", "duplicate")

# Reviewer decisions that end a report's lifecycle in the queue.
TERMINAL_DECISIONS = frozenset({"accepted", "not_pursued", "duplicate"})


class ValidationError(ValueError):
    """Raised for input that fails validation at the trust boundary."""


@dataclass
class ReportDraft:
    category: str
    narrative: str
    state_name: str
    lga: str | None = None
    ward: str | None = None
    pu_id: str | None = None
    reporter_type: str = "citizen"
    channel: str = "web"
    evidence_kind: str = "text_only"
    evidence_sha256: str | None = None
    evidence_b64: str | None = None
    severity_reported: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    spread_score: float = 0.0
    occurred_at: str | None = None


class ShaidaService:
    """Facade over the deterministic core and the assistive components."""

    def __init__(self, settings: Settings | None = None, data_dir: Path | None = None) -> None:
        self.settings = settings or load_settings()
        base = data_dir or self.settings.data_dir
        self.data_dir = base
        self.official_dir = base / "official-synthetic"
        self.evidence_dir = base / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        self.store = Store(self.settings.db_path)
        self.clusterer = Clusterer(threshold=0.55)

        self._claims: list = []
        self.matcher = ClaimMatcher(
            [], self.settings.match_min_similarity, self.settings.match_abstain_below
        )
        self.severity_assist = SeverityAssist(self.settings.classifier_abstain_below)
        self.dataset_status: dict[str, Any] = {}

        self._load_datasets()
        self._rebuild_clusterer_from_store()

    # ----------------------------------------------------------------------------------
    # Dataset loading
    # ----------------------------------------------------------------------------------

    def _load_datasets(self) -> None:
        d = self.official_dir
        status: dict[str, Any] = {"loaded": [], "missing": []}

        def _try(name: str, fn, *paths):
            target = d / paths[0]
            if not target.exists():
                status["missing"].append(str(target))
                return None
            try:
                result = fn(target)
            except Exception as exc:  # a corrupt file must not silently degrade behaviour
                status["missing"].append(f"{target} ({exc.__class__.__name__}: {exc})")
                return None
            status["loaded"].append(name)
            return result

        claims = _try("claims", load_claims, "misinformation_claims_synthetic.jsonl")
        if claims:
            self._claims = claims
            self.matcher = ClaimMatcher(
                claims,
                self.settings.match_min_similarity,
                self.settings.match_abstain_below,
            ).fit()
            status["claims"] = len(claims)

        incidents = _try("incidents", load_incidents, "incident_reports_synthetic.csv")
        if incidents:
            self.severity_assist.train(
                [i.description for i in incidents], [i.severity for i in incidents]
            )
            status["incidents"] = len(incidents)
            status["severity_assist_trained_on"] = self.severity_assist.trained_on
            status["severity_assist_train_accuracy"] = self.severity_assist.train_accuracy

        polling_units = _try("polling_units", load_polling_units, "polling_units_synthetic.csv")
        self.polling_units = polling_units or {}

        results = _try("results", load_results, "results_synthetic.csv")
        self.official_results = results or []

        labels = _try("anomaly_labels", load_anomaly_labels, "anomaly_labels_HELD_OUT.csv")
        self.official_labels = labels or {}

        self.dataset_status = status

    def _rebuild_clusterer_from_store(self) -> None:
        """Rehydrate clustering state so it survives a restart."""
        existing = self.store.list_reports(limit=10_000)
        for report in reversed(existing):  # oldest first
            self.clusterer.assign(report["id"], report["category"], report["narrative"])

    # ----------------------------------------------------------------------------------
    # Validation helpers
    # ----------------------------------------------------------------------------------

    def _validate_report(self, draft: ReportDraft) -> None:
        if draft.category not in INCIDENT_CATEGORIES:
            raise ValidationError(
                f"unknown category {draft.category!r}; expected one of {', '.join(INCIDENT_CATEGORIES)}"
            )
        if draft.reporter_type not in REPORTER_TYPES:
            raise ValidationError(
                f"unknown reporter_type {draft.reporter_type!r}; expected one of "
                f"{', '.join(REPORTER_TYPES)}"
            )
        if draft.evidence_kind not in EVIDENCE_KINDS:
            raise ValidationError(
                f"unknown evidence_kind {draft.evidence_kind!r}; expected one of "
                f"{', '.join(EVIDENCE_KINDS)}"
            )
        text = (draft.narrative or "").strip()
        if len(text) < 10:
            raise ValidationError("narrative must be at least 10 characters")
        if len(text) > self.settings.max_report_chars:
            raise ValidationError(
                f"narrative exceeds the {self.settings.max_report_chars}-character limit"
            )
        if not (draft.state_name or "").strip():
            raise ValidationError("state_name is required")
        if draft.severity_reported is not None and not (0 <= draft.severity_reported <= 4):
            raise ValidationError("severity_reported must be between 0 and 4")
        if draft.evidence_sha256 and not _SHA256_HEX.match(draft.evidence_sha256):
            raise ValidationError("evidence_sha256 must be 64 lowercase hex characters")
        if (draft.latitude is None) != (draft.longitude is None):
            raise ValidationError("latitude and longitude must be supplied together or not at all")
        if draft.latitude is not None and not (-90 <= draft.latitude <= 90):
            raise ValidationError("latitude out of range")
        if draft.longitude is not None and not (-180 <= draft.longitude <= 180):
            raise ValidationError("longitude out of range")

    @staticmethod
    def _coarsen_location(lat: float | None, lon: float | None) -> str | None:
        """Reduce coordinates to ~0.01° (~1.1 km) to avoid endangering a reporter.

        The Track 5 brief forbids location precision that could endanger observers, so exact
        coordinates are never stored or returned.
        """
        if lat is None or lon is None:
            return None
        return f"{round(lat, 2):.2f},{round(lon, 2):.2f}"

    def _store_evidence(self, b64: str, declared_sha: str | None) -> tuple[str, bool]:
        """Decode, hash and persist an evidence blob. Returns ``(sha256, stored)``."""
        try:
            raw = base64.b64decode(b64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValidationError("evidence_b64 is not valid base64") from exc
        if len(raw) > 5_000_000:
            raise ValidationError("evidence exceeds the 5 MB limit")
        digest = hashlib.sha256(raw).hexdigest()
        if declared_sha and declared_sha != digest:
            raise ValidationError(
                "declared evidence_sha256 does not match the uploaded evidence; refusing to "
                "record a hash that the evidence does not produce"
            )
        target = self.evidence_dir / digest
        if not target.exists():
            target.write_bytes(raw)
        return digest, True

    # ----------------------------------------------------------------------------------
    # Reports
    # ----------------------------------------------------------------------------------

    def create_report(self, draft: ReportDraft) -> dict[str, Any]:
        self._validate_report(draft)

        evidence_sha: str | None = None
        evidence_stored = False
        if draft.evidence_b64:
            evidence_sha, evidence_stored = self._store_evidence(
                draft.evidence_b64, draft.evidence_sha256
            )
        elif draft.evidence_sha256:
            evidence_sha = draft.evidence_sha256
        has_evidence = bool(evidence_sha)

        narrative = draft.narrative.strip()
        severity_estimated, confidence, assist_detail = self.severity_assist.predict(narrative)

        mentions_procedure = bool(_PROCEDURAL_CUES.search(narrative))
        report_id = new_id("rep")
        cluster_id, cluster_size = self.clusterer.assign(
            report_id, draft.category, narrative
        )

        triage = harm_priority(
            TriageInput(
                text=narrative,
                category=draft.category,
                severity_reported=draft.severity_reported,
                severity_estimated=severity_estimated,
                spread_score=draft.spread_score,
                has_evidence=has_evidence,
                mentions_procedure=mentions_procedure,
                age_hours=0.0,
                cluster_size=cluster_size,
            )
        )

        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        is_sensitive = draft.category in SENSITIVE_CATEGORIES
        geo_coarse = self._coarsen_location(draft.latitude, draft.longitude)

        record_for_hash = {
            "category": draft.category,
            "narrative": narrative,
            "state": draft.state_name.strip(),
            "lga": (draft.lga or "").strip() or None,
            "ward": (draft.ward or "").strip() or None,
            "pu_id": (draft.pu_id or "").strip() or None,
            "reporter_type": draft.reporter_type,
            "channel": draft.channel,
            "evidence_kind": draft.evidence_kind,
            "evidence_sha256": evidence_sha,
            "severity_reported": draft.severity_reported,
            "geo_coarse": geo_coarse,
        }
        report_hash = content_hash(record_for_hash)

        report = {
            "id": report_id,
            "created_at": created_at,
            "category": draft.category,
            "severity_reported": draft.severity_reported,
            "severity_estimated": severity_estimated,
            "severity_confidence": round(confidence, 4),
            "severity_assist": assist_detail,
            "state_name": draft.state_name.strip(),
            "lga": (draft.lga or "").strip() or None,
            "ward": (draft.ward or "").strip() or None,
            "pu_id": (draft.pu_id or "").strip() or None,
            "geo_coarse": geo_coarse,
            "narrative": narrative,
            "reporter_type": draft.reporter_type,
            "channel": draft.channel,
            "evidence_kind": draft.evidence_kind,
            "evidence_sha256": evidence_sha,
            "evidence_stored": evidence_stored,
            "has_evidence": has_evidence,
            "is_sensitive": is_sensitive,
            "priority": triage.priority,
            "priority_band": triage.band,
            "triage": {
                "priority": triage.priority,
                "band": triage.band,
                "contributions": triage.contributions,
                "rationale": list(triage.rationale),
                "weights": __import__("shdaida.assist", fromlist=["HARM_WEIGHTS"]).HARM_WEIGHTS,
                "needs_human_review": triage.needs_human_review,
            },
            "content_hash": report_hash,
            "cluster_id": cluster_id,
            "cluster_size": cluster_size,
            "mentions_procedure": mentions_procedure,
        }

        audit_payload = {
            "category": draft.category,
            "state": report["state_name"],
            "pu_id": report["pu_id"],
            "evidence_sha256": evidence_sha,
            "content_hash": report_hash,
            "priority": triage.priority,
            "band": triage.band,
            "cluster_id": cluster_id,
            "severity_reported": draft.severity_reported,
            "severity_estimated": severity_estimated,
            # Deliberately no reporter identity: none was collected.
        }
        self.store.insert_report(report, audit_payload)
        return report

    def list_reports(self, **filters: Any) -> list[dict[str, Any]]:
        return self.store.list_reports(**filters)

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        return self.store.get_report(report_id)

    def review_report(
        self,
        report_id: str,
        reviewer: str,
        decision: str,
        reason: str,
        note: str | None = None,
    ) -> dict[str, Any]:
        if decision not in DECISIONS:
            raise ValidationError(
                f"unknown decision {decision!r}; expected one of {', '.join(DECISIONS)}"
            )
        if not (reviewer or "").strip():
            raise ValidationError("reviewer is required")
        if len((reason or "").strip()) < 5:
            raise ValidationError("a reason of at least 5 characters is required for any decision")
        if self.store.get_report(report_id) is None:
            raise LookupError(f"report {report_id} not found")

        action = {
            "id": new_id("rev"),
            "report_id": report_id,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "reviewer": reviewer.strip()[:64],
            "decision": decision,
            "reason": reason.strip()[:500],
            "note": (note or "").strip()[:1000] or None,
        }
        audit = self.store.add_review_action(action)
        return {"review": action, "audit": audit}

    def verify_report(self, report_id: str) -> dict[str, Any]:
        """Independently recompute a report's content hash and confirm it matches."""
        report = self.store.get_report(report_id)
        if report is None:
            raise LookupError(f"report {report_id} not found")
        recomputed = content_hash(
            {
                "category": report["category"],
                "narrative": report["narrative"],
                "state": report["state"],
                "lga": report["lga"],
                "ward": report["ward"],
                "pu_id": report["pu_id"],
                "reporter_type": report["reporter_type"],
                "channel": report["channel"],
                "evidence_kind": report["evidence_kind"],
                "evidence_sha256": report["evidence_sha256"],
                "severity_reported": report["severity_reported"],
                "geo_coarse": report["geo_coarse"],
            }
        )
        return {
            "report_id": report_id,
            "stored_content_hash": report["content_hash"],
            "recomputed_content_hash": recomputed,
            "matches": recomputed == report["content_hash"],
            "method": "sha256 over canonical JSON of the report's content fields",
            "note": (
                "Recomputed from stored fields with no trust in the original writer. "
                "A mismatch means the stored record no longer produces the hash it was "
                "committed under."
            ),
        }

    def verify_audit(self) -> dict[str, Any]:
        verdict = self.store.verify_audit_chain()
        return {
            "intact": verdict.intact,
            "entries_checked": verdict.checked,
            "first_broken_seq": verdict.first_broken_seq,
            "reason": verdict.reason,
            "method": "SHA-256 hash chain over append-only audit entries",
        }

    def explain_report(self, report_id: str, language: str = "en") -> dict[str, Any]:
        report = self.store.get_report(report_id)
        if report is None:
            raise LookupError(f"report {report_id} not found")
        return {
            "report_id": report_id,
            "triage_rationale": report["triage"].get("rationale", []),
            "priority": report["priority"],
            "band": report["priority_band"],
            "language_supported": list(SUPPORTED_LANGUAGES),
        }

    # ----------------------------------------------------------------------------------
    # Result records
    # ----------------------------------------------------------------------------------

    def check_single(self, rec: ResultRecord) -> RuleReport:
        return check_record(rec)

    def ingest_results(
        self, records: Sequence[ResultRecord], persist: bool = True
    ) -> dict[str, Any]:
        reports = check_batch(records)
        rows: list[dict[str, Any]] = []
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for rec, report in zip(records, reports):
            findings = [
                {
                    "rule": f.rule,
                    "tier": f.tier,
                    "severity": f.severity,
                    "message": f.message,
                    "detail": f.detail,
                    "benign_explanations": list(f.benign_explanations),
                    "evidence_refs": list(f.evidence_refs),
                }
                for f in report.findings
            ]
            payload = {
                "pu_id": rec.pu_id,
                "registered_voters": rec.registered_voters,
                "accredited_voters": rec.accredited_voters,
                "rejected_votes": rec.rejected_votes,
                "votes": rec.votes,
            }
            rows.append(
                {
                    "id": new_id("res"),
                    "pu_id": rec.pu_id,
                    "registered_voters": rec.registered_voters,
                    "accredited_voters": rec.accredited_voters,
                    "rejected_votes": rec.rejected_votes,
                    "votes": rec.votes,
                    "rule_report": {
                        "pu_id": rec.pu_id,
                        "findings": findings,
                        "checks_run": list(report.checks_run),
                        "structural_count": report.structural_count,
                        "advisory_count": report.advisory_count,
                    },
                    "content_hash": content_hash(payload),
                    "created_at": created_at,
                }
            )
        if persist:
            self.store.insert_result_records(rows)
        flagged = sum(1 for r in rows if r["rule_report"]["findings"])
        return {
            "ingested": len(rows),
            "flagged": flagged,
            "flag_rate": round(flagged / len(rows), 4) if rows else 0.0,
            "checks_run": list(reports[0].checks_run) if reports else [],
            "records": [
                {
                    "pu_id": r["pu_id"],
                    "content_hash": r["content_hash"],
                    "rule_report": r["rule_report"],
                }
                for r in rows
            ],
        }

    def load_official_results_into_store(self) -> dict[str, Any]:
        if not self.official_results:
            raise LookupError("official synthetic results are not available")
        return self.ingest_results(self.official_results)

    # ----------------------------------------------------------------------------------
    # Claims
    # ----------------------------------------------------------------------------------

    def match_claim(self, query: str, language: str | None = None) -> dict[str, Any]:
        if not (query or "").strip():
            raise ValidationError("query must not be empty")
        if len(query) > self.settings.max_report_chars:
            raise ValidationError("query is too long")
        result = self.matcher.match(query)
        return {
            "query_language": language,
            "abstained": result.abstained,
            "reason": result.reason,
            "top_similarity": round(result.top_similarity, 4),
            "archive_size": len(self._claims),
            "matches": [
                {
                    "claim_id": m.claim_id,
                    "similarity": m.similarity,
                    "archived_label": m.label,
                    "language": m.language,
                    "channel": m.channel,
                    "verdict_summary": m.verdict_summary,
                }
                for m in result.matched
            ],
            "caveat": (
                "A match means an archived claim looks similar. It is not a statement about "
                "whether this claim is true, and a human must confirm any match before it is used."
            ),
        }

    def explain_findings(self, findings: Iterable[Any], language: str = "en") -> dict[str, Any]:
        return explain_findings(findings, language)

    # ----------------------------------------------------------------------------------
    # Aggregation and stats
    # ----------------------------------------------------------------------------------

    def aggregate(self, group_by: str = "state", min_count: int | None = None) -> dict[str, Any]:
        floor = min_count if min_count is not None else self.settings.k_anonymity_floor
        payload = self.store.aggregate_counts(group_by, floor)[0]
        payload["group_by"] = group_by
        payload["privacy_note"] = (
            f"Cells with fewer than {floor} reports are suppressed entirely, so no individual "
            f"report can be recovered from the aggregate."
        )
        return payload

    def stats(self) -> dict[str, Any]:
        base = self.store.stats()
        base["dataset_status"] = self.dataset_status
        base["clusters"] = len(self.clusterer.clusters)
        base["archive_claims"] = len(self._claims)
        base["severity_assist_available"] = self.severity_assist.available
        return base

    def cluster_summary(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.clusterer.summary()[:limit]
