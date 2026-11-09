"""HTTP API for SHAIDA.

Security posture:
  * Input validation happens at the boundary via Pydantic models with hard bounds, so
    malformed or oversized input never reaches the service layer.
  * Write endpoints are rate-limited per client to blunt report flooding.
  * Reviewer endpoints require an explicit reviewer identity and a reason, and every action
    is written to the append-only audit log.
  * Errors return a stable ``{"error": {"code", "message"}}`` shape and never leak stack
    traces or internal paths.
  * CORS is restricted to the configured origins (default: the local frontend only).
  * No endpoint accepts or returns reporter identity, because none is collected.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from . import __version__
from .config import ConfigError, load_settings
from .rules import ResultRecord, arithmetic_certificate
from .service import (
    DECISIONS,
    ReportDraft,
    ShaidaService,
    ValidationError,
)
from .taxonomy import EVIDENCE_KINDS, INCIDENT_CATEGORIES, REPORTER_TYPES

# --------------------------------------------------------------------------------------
# Request models (validation at the trust boundary)
# --------------------------------------------------------------------------------------


class ReportIn(BaseModel):
    category: Literal[tuple(INCIDENT_CATEGORIES)]  # type: ignore[valid-type]
    narrative: str = Field(min_length=10, max_length=2000)
    state_name: str = Field(min_length=2, max_length=64)
    lga: str | None = Field(default=None, max_length=64)
    ward: str | None = Field(default=None, max_length=64)
    pu_id: str | None = Field(default=None, max_length=32)
    reporter_type: Literal[tuple(REPORTER_TYPES)] = "citizen"  # type: ignore[valid-type]
    channel: str = Field(default="web", max_length=32)
    evidence_kind: Literal[tuple(EVIDENCE_KINDS)] = "text_only"  # type: ignore[valid-type]
    evidence_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    evidence_b64: str | None = None
    severity_reported: int | None = Field(default=None, ge=0, le=4)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    spread_score: float = Field(default=0.0, ge=0.0, le=100.0)
    occurred_at: str | None = Field(default=None, max_length=32)

    @field_validator("narrative")
    @classmethod
    def _no_control_chars(cls, value: str) -> str:
        cleaned = "".join(ch for ch in value if ch == "\n" or ch >= " ")
        if len(cleaned.strip()) < 10:
            raise ValueError("narrative must be at least 10 characters of visible text")
        return cleaned


class ReviewIn(BaseModel):
    reviewer: str = Field(min_length=2, max_length=64)
    decision: Literal[tuple(DECISIONS)]  # type: ignore[valid-type]
    reason: str = Field(min_length=5, max_length=500)
    note: str | None = Field(default=None, max_length=1000)


class ResultRecordIn(BaseModel):
    pu_id: str = Field(min_length=1, max_length=32)
    registered_voters: int = Field(ge=0, le=10_000_000)
    accredited_voters: int = Field(ge=0, le=10_000_000)
    rejected_votes: int = Field(ge=0, le=10_000_000)
    votes: dict[str, int]

    @field_validator("votes")
    @classmethod
    def _bound_votes(cls, value: dict[str, int]) -> dict[str, int]:
        if len(value) > 64:
            raise ValueError("at most 64 candidate tallies are accepted")
        for key, tally in value.items():
            if len(key) > 16:
                raise ValueError(f"candidate key {key!r} is too long")
            if not isinstance(tally, int) or tally < 0 or tally > 10_000_000:
                raise ValueError(f"tally for {key!r} must be an integer in [0, 10_000_000]")
        return value


class ResultBatchIn(BaseModel):
    records: list[ResultRecordIn] = Field(min_length=1, max_length=5000)


class ClaimIn(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    language: str | None = Field(default=None, max_length=8)


class ExplainIn(BaseModel):
    language: Literal["en", "pcm", "ha", "yo", "ig"] = "en"


# --------------------------------------------------------------------------------------
# Rate limiting
# --------------------------------------------------------------------------------------


class RateLimiter:
    """Simple sliding-window limiter keyed by client host.

    Deliberately in-process: the prototype is single-node, and adding Redis would be an
    unjustified dependency. It exists to blunt accidental and trivial flooding, and the
    limitation is documented rather than overstated.
    """

    def __init__(self, per_minute: int) -> None:
        self.per_minute = per_minute
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> tuple[bool, int]:
        now = time.monotonic()
        window = self._hits[key]
        while window and now - window[0] > 60.0:
            window.popleft()
        if len(window) >= self.per_minute:
            return False, 0
        window.append(now)
        return True, self.per_minute - len(window)


# --------------------------------------------------------------------------------------
# Application factory
# --------------------------------------------------------------------------------------


def create_app(service: ShaidaService | None = None) -> FastAPI:
    try:
        settings = load_settings()
    except ConfigError as exc:  # fail fast and loudly on bad configuration
        raise SystemExit(f"SHAIDA configuration error: {exc}") from exc

    svc = service or ShaidaService(settings)
    limiter = RateLimiter(settings.write_rate_limit_per_minute)

    app = FastAPI(
        title="SHAIDA API",
        version=__version__,
        description=(
            "Verifiable electoral evidence and triage. Deterministic verification with "
            "narrowly-scoped, abstaining AI assistance. Flags only — never verdicts."
        ),
    )
    app.state.service = svc
    app.state.limiter = limiter

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    # -- error handling: stable shape, no internals leaked ------------------------------

    @app.exception_handler(ValidationError)
    async def _validation_handler(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": {"code": "invalid_input", "message": str(exc)}},
        )

    @app.exception_handler(LookupError)
    async def _not_found_handler(_: Request, exc: LookupError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"code": "not_found", "message": str(exc)}},
        )

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:  # pragma: no cover
        # Never expose the exception text: it can contain file paths or library internals.
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "The server could not complete the request.",
                }
            },
        )

    def _enforce_rate_limit(request: Request) -> None:
        client = request.client.host if request.client else "unknown"
        allowed, remaining = limiter.allow(client)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit reached ({limiter.per_minute} writes/minute). Try again shortly.",
            )

    # -- health ------------------------------------------------------------------------

    @app.get("/v1/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "version": __version__,
            "service": "shaida",
            "human_review_required": True,
            "declares_results": False,
        }

    @app.get("/v1/stats")
    def stats() -> dict[str, Any]:
        return svc.stats()

    @app.get("/v1/datasets")
    def datasets() -> dict[str, Any]:
        return svc.dataset_status

    # -- reports -----------------------------------------------------------------------

    @app.post("/v1/reports", status_code=status.HTTP_201_CREATED)
    def create_report(payload: ReportIn, request: Request) -> dict[str, Any]:
        _enforce_rate_limit(request)
        draft = ReportDraft(
            category=payload.category,
            narrative=payload.narrative,
            state_name=payload.state_name,
            lga=payload.lga,
            ward=payload.ward,
            pu_id=payload.pu_id,
            reporter_type=payload.reporter_type,
            channel=payload.channel,
            evidence_kind=payload.evidence_kind,
            evidence_sha256=payload.evidence_sha256,
            evidence_b64=payload.evidence_b64,
            severity_reported=payload.severity_reported,
            latitude=payload.latitude,
            longitude=payload.longitude,
            spread_score=payload.spread_score,
            occurred_at=payload.occurred_at,
        )
        report = svc.create_report(draft)
        # Never echo the raw narrative back with internal fields; return the public view.
        return {
            "id": report["id"],
            "created_at": report["created_at"],
            "category": report["category"],
            "priority": report["priority"],
            "priority_band": report["priority_band"],
            "triage": report["triage"],
            "content_hash": report["content_hash"],
            "cluster_id": report["cluster_id"],
            "cluster_size": report["cluster_size"],
            "evidence_sha256": report["evidence_sha256"],
            "severity_estimated": report["severity_estimated"],
            "severity_confidence": report["severity_confidence"],
            "is_sensitive": report["is_sensitive"],
            "review_required": True,
            "message": (
                "Recorded and hashed. A human reviewer must adjudicate this report; SHAIDA "
                "has not made any finding about it."
            ),
        }

    @app.get("/v1/reports")
    def list_reports(
        limit: int = Query(default=50, ge=1, le=500),
        state: str | None = Query(default=None, max_length=64),
        category: str | None = Query(default=None, max_length=64),
        band: str | None = Query(default=None, max_length=16),
        review_state: Literal["pending", "reviewed"] | None = None,
    ) -> dict[str, Any]:
        items = svc.list_reports(
            limit=limit, state=state, category=category, band=band, review_state=review_state
        )
        return {"count": len(items), "reports": items}

    @app.get("/v1/reports/{report_id}")
    def get_report(report_id: str) -> dict[str, Any]:
        report = svc.get_report(report_id)
        if report is None:
            raise LookupError(f"report {report_id} not found")
        return report

    @app.get("/v1/reports/{report_id}/verify")
    def verify_report(report_id: str) -> dict[str, Any]:
        return svc.verify_report(report_id)

    @app.get("/v1/reports/{report_id}/explain")
    def explain_report(
        report_id: str, language: Literal["en", "pcm", "ha", "yo", "ig"] = "en"
    ) -> dict[str, Any]:
        return svc.explain_report(report_id, language)

    @app.post("/v1/reports/{report_id}/review", status_code=status.HTTP_201_CREATED)
    def review_report(report_id: str, payload: ReviewIn, request: Request) -> dict[str, Any]:
        _enforce_rate_limit(request)
        return svc.review_report(
            report_id, payload.reviewer, payload.decision, payload.reason, payload.note
        )

    # -- results -----------------------------------------------------------------------

    @app.post("/v1/results/check")
    def check_results(payload: ResultBatchIn, request: Request) -> dict[str, Any]:
        _enforce_rate_limit(request)
        records = [
            ResultRecord(
                pu_id=r.pu_id,
                registered_voters=r.registered_voters,
                accredited_voters=r.accredited_voters,
                votes=r.votes,
                rejected_votes=r.rejected_votes,
            )
            for r in payload.records
        ]
        return svc.ingest_results(records)

    @app.post("/v1/results/load-official")
    def load_official_results(request: Request) -> dict[str, Any]:
        _enforce_rate_limit(request)
        return svc.load_official_results_into_store()

    @app.get("/v1/results")
    def list_results(
        only_flagged: bool = False, limit: int = Query(default=200, ge=1, le=2000)
    ) -> dict[str, Any]:
        items = svc.store.list_result_records(only_flagged=only_flagged, limit=limit)
        return {"count": len(items), "records": items}

    @app.get("/v1/results/{pu_id}")
    def get_result(pu_id: str) -> dict[str, Any]:
        record = svc.store.get_result_record(pu_id)
        if record is None:
            raise LookupError(f"no result record for {pu_id}")
        return record

    @app.get("/v1/results/{pu_id}/certificate")
    def result_certificate(pu_id: str) -> dict[str, Any]:
        record = svc.store.get_result_record(pu_id)
        if record is None:
            raise LookupError(f"no result record for {pu_id}")
        return arithmetic_certificate(
            ResultRecord(
                pu_id=record["pu_id"],
                registered_voters=record["registered_voters"],
                accredited_voters=record["accredited_voters"],
                votes=record["votes"],
                rejected_votes=record["rejected_votes"],
            )
        )

    # -- claims ------------------------------------------------------------------------

    @app.post("/v1/claims/match")
    def match_claim(payload: ClaimIn, request: Request) -> dict[str, Any]:
        _enforce_rate_limit(request)
        return svc.match_claim(payload.query, payload.language)

    # -- integrity ---------------------------------------------------------------------

    @app.get("/v1/integrity/audit")
    def audit_chain(limit: int = Query(default=50, ge=1, le=500)) -> dict[str, Any]:
        verdict = svc.verify_audit()
        verdict["entries"] = svc.store.audit_entries(limit)
        return verdict

    @app.get("/v1/aggregate")
    def aggregate(
        group_by: Literal["state", "category", "band"] = "state",
        min_count: int | None = Query(default=None, ge=2, le=100),
    ) -> dict[str, Any]:
        return svc.aggregate(group_by, min_count)

    @app.get("/v1/clusters")
    def clusters(limit: int = Query(default=20, ge=1, le=200)) -> dict[str, Any]:
        return {"clusters": svc.cluster_summary(limit)}

    return app


app = create_app()
