"""API integration tests: validation, error shapes, rate limiting, and the no-verdict rule.

These drive the real FastAPI application through ``TestClient``, so they exercise the actual
request path (Pydantic validation, exception handlers, service layer, storage) rather than a
mocked one.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from shdaida.api import RateLimiter, create_app
from shdaida.config import Settings
from shdaida.service import ShaidaService


@pytest.fixture()
def client(tmp_path):
    settings = Settings(
        db_path=tmp_path / "api.sqlite3",
        data_dir=tmp_path,
        k_anonymity_floor=3,
        match_min_similarity=0.35,
        match_abstain_below=0.45,
        classifier_abstain_below=0.55,
        write_rate_limit_per_minute=1000,
        max_report_chars=2000,
    )
    service = ShaidaService(settings, data_dir=tmp_path)
    app = create_app(service)
    with TestClient(app) as test_client:
        yield test_client


VALID_REPORT = {
    "category": "logistics_delay",
    "narrative": "Materials had not arrived at the unit by 9am and about 200 people were waiting.",
    "state_name": "Ogun",
    "reporter_type": "observer",
}


# --------------------------------------------------------------------------------------
# Health and discovery
# --------------------------------------------------------------------------------------


def test_health_declares_no_verdict_capability(client):
    body = client.get("/v1/health").json()
    assert body["status"] == "ok"
    assert body["declares_results"] is False
    assert body["human_review_required"] is True


# --------------------------------------------------------------------------------------
# Report lifecycle
# --------------------------------------------------------------------------------------


def test_create_report_returns_hash_and_reference(client):
    response = client.post("/v1/reports", json=VALID_REPORT)
    assert response.status_code == 201
    body = response.json()
    assert body["id"].startswith("rep-")
    assert len(body["content_hash"]) == 64
    assert body["review_required"] is True
    assert "reviewer" in body["message"]


def test_created_report_can_be_retrieved_and_verified(client):
    report_id = client.post("/v1/reports", json=VALID_REPORT).json()["id"]
    fetched = client.get(f"/v1/reports/{report_id}")
    assert fetched.status_code == 200
    assert fetched.json()["narrative"] == VALID_REPORT["narrative"]

    verdict = client.get(f"/v1/reports/{report_id}/verify").json()
    assert verdict["matches"] is True
    assert verdict["recomputed_content_hash"] == verdict["stored_content_hash"]


def test_no_reporter_identity_is_stored(client):
    """The schema has no identity field, and none must appear in any response."""
    report_id = client.post("/v1/reports", json=VALID_REPORT).json()["id"]
    body = client.get(f"/v1/reports/{report_id}").json()
    for forbidden in ("name", "email", "phone", "reporter_id", "user_id", "ip"):
        assert forbidden not in body, f"{forbidden} must never be stored on a report"


def test_sensitive_category_is_flagged_for_extra_handling(client):
    body = client.post(
        "/v1/reports",
        json={**VALID_REPORT, "category": "violence_or_threat", "severity_reported": 4},
    ).json()
    assert body["is_sensitive"] is True
    assert body["priority_band"] in {"urgent", "high"}


def test_coordinates_are_coarsened_and_never_returned_exactly(client):
    body = client.post(
        "/v1/reports",
        json={**VALID_REPORT, "latitude": 6.524379, "longitude": 3.379205},
    ).json()
    report = client.get(f"/v1/reports/{body['id']}").json()
    assert report["geo_coarse"] == "6.52,3.38"
    assert "6.524379" not in str(report)


# --------------------------------------------------------------------------------------
# Validation at the boundary
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload, reason",
    [
        ({**VALID_REPORT, "category": "not_a_category"}, "unknown category"),
        ({**VALID_REPORT, "narrative": "short"}, "narrative too short"),
        ({**VALID_REPORT, "state_name": ""}, "empty state"),
        ({**VALID_REPORT, "reporter_type": "stranger"}, "unknown reporter type"),
        ({**VALID_REPORT, "severity_reported": 9}, "severity out of range"),
        ({**VALID_REPORT, "latitude": 6.5}, "latitude without longitude"),
        ({**VALID_REPORT, "evidence_sha256": "zz"}, "bad hash format"),
    ],
)
def test_invalid_input_is_rejected_with_422(client, payload, reason):
    response = client.post("/v1/reports", json=payload)
    assert response.status_code == 422, reason


def test_narrative_over_the_limit_is_rejected(client):
    response = client.post("/v1/reports", json={**VALID_REPORT, "narrative": "x" * 3000})
    assert response.status_code == 422


def test_error_shape_is_stable_and_leaks_nothing(client):
    response = client.post("/v1/reports", json={**VALID_REPORT, "category": "bogus"})
    body = response.json()
    assert "detail" in body or "error" in body
    assert "Traceback" not in response.text
    assert "/workspace" not in response.text


def test_unknown_report_returns_404(client):
    assert client.get("/v1/reports/rep-does-not-exist").status_code == 404


# --------------------------------------------------------------------------------------
# Review workflow
# --------------------------------------------------------------------------------------


def test_review_requires_a_reason(client):
    report_id = client.post("/v1/reports", json=VALID_REPORT).json()["id"]
    response = client.post(
        f"/v1/reports/{report_id}/review",
        json={"reviewer": "R. Reviewer", "decision": "accepted", "reason": "no"},
    )
    assert response.status_code == 422


def test_review_is_recorded_and_audited(client):
    report_id = client.post("/v1/reports", json=VALID_REPORT).json()["id"]
    response = client.post(
        f"/v1/reports/{report_id}/review",
        json={
            "reviewer": "R. Reviewer",
            "decision": "needs_more_evidence",
            "reason": "Asked the observer for the sheet photograph.",
        },
    )
    assert response.status_code == 201
    assert response.json()["review"]["decision"] == "needs_more_evidence"

    report = client.get(f"/v1/reports/{report_id}").json()
    assert len(report["review_actions"]) == 1

    audit = client.get("/v1/integrity/audit").json()
    assert audit["intact"] is True
    assert any(entry["action"] == "report.reviewed" for entry in audit["entries"])


def test_review_rejects_unknown_decision(client):
    report_id = client.post("/v1/reports", json=VALID_REPORT).json()["id"]
    response = client.post(
        f"/v1/reports/{report_id}/review",
        json={"reviewer": "R", "decision": "convicted", "reason": "not a real decision"},
    )
    assert response.status_code == 422


# --------------------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------------------


def test_result_check_accepts_a_batch_and_flags_arithmetic(client):
    response = client.post(
        "/v1/results/check",
        json={
            "records": [
                {
                    "pu_id": "SIM-00001",
                    "registered_voters": 1000,
                    "accredited_voters": 500,
                    "rejected_votes": 10,
                    "votes": {"A": 490},
                },
                {
                    "pu_id": "SIM-00002",
                    "registered_voters": 1000,
                    "accredited_voters": 100,
                    "rejected_votes": 0,
                    "votes": {"A": 900},
                },
            ]
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ingested"] == 2
    assert body["flagged"] == 1


def test_result_batch_rejects_negative_tally_at_the_boundary(client):
    response = client.post(
        "/v1/results/check",
        json={
            "records": [
                {
                    "pu_id": "SIM-1",
                    "registered_voters": 10,
                    "accredited_voters": 5,
                    "rejected_votes": 0,
                    "votes": {"A": -5},
                }
            ]
        },
    )
    assert response.status_code == 422


def test_certificate_is_available_for_a_stored_record(client):
    client.post(
        "/v1/results/check",
        json={
            "records": [
                {
                    "pu_id": "SIM-00007",
                    "registered_voters": 100,
                    "accredited_voters": 50,
                    "rejected_votes": 5,
                    "votes": {"A": 45},
                }
            ]
        },
    )
    cert = client.get("/v1/results/SIM-00007/certificate").json()
    assert cert["all_balance"] is True
    assert len(cert["lines"]) >= 4


# --------------------------------------------------------------------------------------
# Privacy
# --------------------------------------------------------------------------------------


def test_aggregation_suppresses_small_cells(client):
    for index in range(4):
        client.post("/v1/reports", json={**VALID_REPORT, "state_name": "Kano"})
    client.post("/v1/reports", json={**VALID_REPORT, "state_name": "Enugu"})

    body = client.get("/v1/aggregate?group_by=state").json()
    assert body["min_count"] == 3
    keys = {group["key"] for group in body["groups"]}
    assert "Kano" in keys
    assert "Enugu" not in keys, "a cell below the floor must be suppressed entirely"
    assert body["suppressed_cells"] >= 1


# --------------------------------------------------------------------------------------
# Claims
# --------------------------------------------------------------------------------------


def test_claim_match_abstains_on_unrelated_text(client):
    body = client.post(
        "/v1/claims/match", json={"query": "fertiliser subsidy distribution in Kebbi state"}
    ).json()
    assert "abstained" in body
    assert "caveat" in body


def test_claim_match_rejects_empty_query(client):
    assert client.post("/v1/claims/match", json={"query": "ab"}).status_code == 422


# --------------------------------------------------------------------------------------
# Rate limiting
# --------------------------------------------------------------------------------------


def test_rate_limiter_blocks_after_the_limit():
    limiter = RateLimiter(per_minute=3)
    assert [limiter.allow("host")[0] for _ in range(3)] == [True, True, True]
    allowed, _ = limiter.allow("host")
    assert allowed is False


def test_rate_limiter_is_per_client():
    limiter = RateLimiter(per_minute=1)
    assert limiter.allow("a")[0] is True
    assert limiter.allow("b")[0] is True
    assert limiter.allow("a")[0] is False


# --------------------------------------------------------------------------------------
# No-verdict guarantee across the whole API surface
# --------------------------------------------------------------------------------------


def test_no_api_response_uses_verdict_language(client):
    from shdaida.taxonomy import FORBIDDEN_VERDICT_TERMS

    report_id = client.post("/v1/reports", json=VALID_REPORT).json()["id"]
    payloads = [
        client.get("/v1/health").text,
        client.get(f"/v1/reports/{report_id}").text,
        client.get(f"/v1/reports/{report_id}/verify").text,
        client.get(f"/v1/reports/{report_id}/explain").text,
        client.get("/v1/integrity/audit").text,
    ]
    for payload in payloads:
        lowered = payload.lower()
        for term in FORBIDDEN_VERDICT_TERMS:
            assert term not in lowered, f"response contained verdict term {term!r}"
