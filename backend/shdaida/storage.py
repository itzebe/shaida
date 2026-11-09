"""SQLite persistence with an append-only, hash-chained audit log.

Why SQLite: the prototype must run offline, on free infrastructure, with no service to
provision and no credentials. SQLite gives durable, transactional storage in a single file
that a judge can inspect, and it makes the whole system reproducible from a fresh clone.

The ``audit_log`` table is append-only by construction:
  * rows are never updated or deleted by application code;
  * each row's ``chain_hash`` commits to the previous row's ``chain_hash``;
  * a tampering test mutates a row and proves :func:`verify_audit_chain` fails.

Personal-data posture (NDPA 2023 alignment): reports store **no reporter identity**. There is
no name, phone, email or account column. Location is stored at ward granularity by default,
with coordinates optional, rounded, and only ever exposed through a k-anonymity threshold.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Sequence

from .provenance import ChainEntry, build_chain, content_hash, verify_chain

_SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS audit_log (
    seq           INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id      TEXT    NOT NULL UNIQUE,
    action        TEXT    NOT NULL,
    subject_type  TEXT    NOT NULL,
    subject_id    TEXT    NOT NULL,
    actor_role    TEXT    NOT NULL,
    payload_hash  TEXT    NOT NULL,
    payload       TEXT    NOT NULL,
    created_at    TEXT    NOT NULL,
    prev_chain    TEXT    NOT NULL,
    chain_hash    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
    id                 TEXT PRIMARY KEY,
    created_at         TEXT NOT NULL,
    category           TEXT NOT NULL,
    severity_reported  INTEGER,
    severity_estimated INTEGER,
    severity_confidence REAL,
    state              TEXT NOT NULL,
    lga                TEXT,
    ward               TEXT,
    pu_id              TEXT,
    geo_coarse         TEXT,
    narrative          TEXT NOT NULL,
    reporter_type      TEXT NOT NULL,
    channel            TEXT NOT NULL,
    evidence_kind      TEXT NOT NULL,
    evidence_sha256    TEXT,
    has_evidence       INTEGER NOT NULL DEFAULT 0,
    is_sensitive       INTEGER NOT NULL DEFAULT 0,
    priority           REAL NOT NULL,
    priority_band      TEXT NOT NULL,
    triage             TEXT NOT NULL,
    content_hash       TEXT NOT NULL,
    cluster_id         TEXT
);
CREATE INDEX IF NOT EXISTS idx_reports_priority ON reports(priority DESC);
CREATE INDEX IF NOT EXISTS idx_reports_state ON reports(state);

CREATE TABLE IF NOT EXISTS review_actions (
    id          TEXT PRIMARY KEY,
    report_id   TEXT NOT NULL REFERENCES reports(id),
    created_at  TEXT NOT NULL,
    reviewer    TEXT NOT NULL,
    decision    TEXT NOT NULL,
    reason      TEXT NOT NULL,
    note        TEXT
);
CREATE INDEX IF NOT EXISTS idx_review_report ON review_actions(report_id);

CREATE TABLE IF NOT EXISTS result_records (
    id                 TEXT PRIMARY KEY,
    pu_id              TEXT NOT NULL,
    registered_voters  INTEGER NOT NULL,
    accredited_voters  INTEGER NOT NULL,
    rejected_votes     INTEGER NOT NULL,
    votes_json         TEXT NOT NULL,
    report_json        TEXT NOT NULL,
    content_hash       TEXT NOT NULL,
    created_at         TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_results_pu ON result_records(pu_id);
"""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True)
class AuditVerdict:
    """Result of verifying the audit chain.

    ``payload_mismatches`` lists entries whose stored payload no longer re-hashes to its
    recorded digest. It is separate from the link-chain verdict because the two failures have
    different meanings: a link break means the history was rewritten, while a payload mismatch
    means a single entry's content was edited in place.
    """

    intact: bool
    checked: int
    first_broken_seq: int | None
    reason: str | None
    payload_mismatches: tuple[int, ...] = ()


@dataclass
class Store:
    """Thread-safe SQLite store. One connection per thread, WAL mode for concurrency."""

    db_path: Path

    def __post_init__(self) -> None:
        self._local = threading.local()
        self._lock = threading.Lock()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(_SCHEMA)
            conn.commit()

    # -- connection handling -----------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = self._connect()
            self._local.conn = conn
        yield conn

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                yield conn
            except Exception:
                conn.execute("ROLLBACK")
                raise
            else:
                conn.execute("COMMIT")

    # -- audit log ---------------------------------------------------------------------

    def _last_chain_hash(self, conn: sqlite3.Connection) -> str:
        row = conn.execute(
            "SELECT chain_hash FROM audit_log ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        return row["chain_hash"] if row else "0" * 64

    def append_audit(
        self,
        action: str,
        subject_type: str,
        subject_id: str,
        actor_role: str,
        payload: dict[str, Any],
        conn: sqlite3.Connection | None = None,
    ) -> dict[str, Any]:
        """Append one audit entry, chaining it to the current head of the log."""
        from .provenance import chain_hash as _chain_hash

        entry_id = new_id("aud")
        payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        payload_digest = content_hash({"payload": json.loads(payload_json)})
        created_at = _utc_now()

        def _do(c: sqlite3.Connection) -> dict[str, Any]:
            prev = self._last_chain_hash(c)
            seq_row = c.execute("SELECT COALESCE(MAX(seq), 0) AS s FROM audit_log").fetchone()
            seq = int(seq_row["s"]) + 1
            link = _chain_hash(prev, payload_digest, seq)
            c.execute(
                """
                INSERT INTO audit_log (seq, entry_id, action, subject_type, subject_id,
                                       actor_role, payload_hash, payload, created_at,
                                       prev_chain, chain_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    seq,
                    entry_id,
                    action,
                    subject_type,
                    subject_id,
                    actor_role,
                    payload_digest,
                    payload_json,
                    created_at,
                    prev,
                    link,
                ),
            )
            return {
                "seq": seq,
                "entry_id": entry_id,
                "action": action,
                "subject_type": subject_type,
                "subject_id": subject_id,
                "payload_hash": payload_digest,
                "chain_hash": link,
                "created_at": created_at,
            }

        if conn is not None:
            return _do(conn)
        with self._lock, self.transaction() as c:
            return _do(c)

    def audit_chain(self) -> list[ChainEntry]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT seq, payload, payload_hash, prev_chain, chain_hash "
                "FROM audit_log ORDER BY seq ASC"
            ).fetchall()
        return [
            ChainEntry(
                seq=int(r["seq"]),
                content_hash=r["payload_hash"],
                prev_chain_hash=r["prev_chain"],
                chain_hash=r["chain_hash"],
            )
            for r in rows
        ]

    def verify_audit_chain(self) -> "AuditVerdict":
        """Recompute the whole audit chain and report the first inconsistency.

        Two independent things are checked, because either alone is insufficient:

        1. **Link integrity** — each entry's ``chain_hash`` is recomputed from the stored
           ``payload_hash`` and the previous link. This catches an attacker who edits a row's
           chain columns.
        2. **Payload integrity** — the stored ``payload`` is re-hashed and compared with the
           stored ``payload_hash``. This catches an attacker who edits the payload text while
           leaving the hash column alone, which link checking by itself would not notice.

        Without (2) the log would only be tamper-evident against someone who does not know to
        leave the hash column untouched, which is not a meaningful guarantee.
        """
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT seq, payload, payload_hash, prev_chain, chain_hash "
                "FROM audit_log ORDER BY seq ASC"
            ).fetchall()

        entries: list[ChainEntry] = []
        payload_mismatches: list[int] = []
        for row in rows:
            entries.append(
                ChainEntry(
                    seq=int(row["seq"]),
                    content_hash=row["payload_hash"],
                    prev_chain_hash=row["prev_chain"],
                    chain_hash=row["chain_hash"],
                )
            )
            try:
                stored_payload = json.loads(row["payload"])
            except json.JSONDecodeError:
                payload_mismatches.append(int(row["seq"]))
                continue
            if content_hash({"payload": stored_payload}) != row["payload_hash"]:
                payload_mismatches.append(int(row["seq"]))

        link_verdict = verify_chain(entries)
        if payload_mismatches:
            first = payload_mismatches[0]
            return AuditVerdict(
                intact=False,
                checked=min(link_verdict.checked, len(entries)),
                first_broken_seq=first,
                reason=(
                    f"payload at seq {first} does not re-hash to its recorded digest "
                    f"(entries altered: {len(payload_mismatches)})"
                ),
                payload_mismatches=tuple(payload_mismatches),
            )
        return AuditVerdict(
            intact=link_verdict.intact,
            checked=link_verdict.checked,
            first_broken_seq=link_verdict.first_broken_seq,
            reason=link_verdict.reason,
            payload_mismatches=(),
        )

    def audit_entries(self, limit: int = 200) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT seq, entry_id, action, subject_type, subject_id, actor_role, "
                "payload_hash, created_at, chain_hash FROM audit_log ORDER BY seq DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    # -- reports -----------------------------------------------------------------------

    def insert_report(self, report: dict[str, Any], audit_payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock, self.transaction() as conn:
            conn.execute(
                """
                INSERT INTO reports (
                    id, created_at, category, severity_reported, severity_estimated,
                    severity_confidence, state, lga, ward, pu_id, geo_coarse, narrative,
                    reporter_type, channel, evidence_kind, evidence_sha256, has_evidence,
                    is_sensitive, priority, priority_band, triage, content_hash, cluster_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report["id"],
                    report["created_at"],
                    report["category"],
                    report["severity_reported"],
                    report["severity_estimated"],
                    report["severity_confidence"],
                    report["state_name"],
                    report["lga"],
                    report["ward"],
                    report["pu_id"],
                    report["geo_coarse"],
                    report["narrative"],
                    report["reporter_type"],
                    report["channel"],
                    report["evidence_kind"],
                    report["evidence_sha256"],
                    1 if report["has_evidence"] else 0,
                    1 if report["is_sensitive"] else 0,
                    report["priority"],
                    report["priority_band"],
                    json.dumps(report["triage"], ensure_ascii=False),
                    report["content_hash"],
                    report.get("cluster_id"),
                ),
            )
            audit = self.append_audit(
                action="report.created",
                subject_type="report",
                subject_id=report["id"],
                actor_role="reporter",
                payload=audit_payload,
                conn=conn,
            )
        return audit

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
            if row is None:
                return None
            actions = conn.execute(
                "SELECT * FROM review_actions WHERE report_id = ? ORDER BY created_at ASC",
                (report_id,),
            ).fetchall()
        report = dict(row)
        report["triage"] = json.loads(report["triage"])
        report["has_evidence"] = bool(report["has_evidence"])
        report["is_sensitive"] = bool(report["is_sensitive"])
        report["review_actions"] = [dict(a) for a in actions]
        return report

    def list_reports(
        self,
        limit: int = 100,
        state: str | None = None,
        category: str | None = None,
        band: str | None = None,
        review_state: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if state:
            clauses.append("state = ?")
            params.append(state)
        if category:
            clauses.append("category = ?")
            params.append(category)
        if band:
            clauses.append("priority_band = ?")
            params.append(band)
        if review_state == "reviewed":
            clauses.append("id IN (SELECT report_id FROM review_actions)")
        elif review_state == "pending":
            clauses.append("id NOT IN (SELECT report_id FROM review_actions)")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.append(limit)
        with self.connection() as conn:
            rows = conn.execute(
                f"SELECT * FROM reports {where} ORDER BY priority DESC, created_at DESC LIMIT ?",
                params,
            ).fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["triage"] = json.loads(item["triage"])
            item["has_evidence"] = bool(item["has_evidence"])
            item["is_sensitive"] = bool(item["is_sensitive"])
            out.append(item)
        return out

    def add_review_action(self, action: dict[str, Any]) -> dict[str, Any]:
        with self._lock, self.transaction() as conn:
            conn.execute(
                """
                INSERT INTO review_actions (id, report_id, created_at, reviewer, decision, reason, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    action["id"],
                    action["report_id"],
                    action["created_at"],
                    action["reviewer"],
                    action["decision"],
                    action["reason"],
                    action.get("note"),
                ),
            )
            audit = self.append_audit(
                action="report.reviewed",
                subject_type="report",
                subject_id=action["report_id"],
                actor_role=action["reviewer"],
                payload={
                    "decision": action["decision"],
                    "reason": action["reason"],
                    "note": action.get("note"),
                    "review_id": action["id"],
                },
                conn=conn,
            )
        return audit

    def aggregate_counts(
        self, group_by: str = "state", min_count: int = 5
    ) -> list[dict[str, Any]]:
        """k-anonymised aggregation.

        Cells with fewer than ``min_count`` reports are **suppressed entirely** (counts
        withheld, not rounded), so a single report can never be re-identified by subtraction.
        This is the privacy-preserving aggregation required by the Track 4 brief (item 4B)
        and the NDPA 2023 minimisation principle.
        """
        allowed = {"state": "state", "category": "category", "band": "priority_band"}
        column = allowed.get(group_by)
        if column is None:
            raise ValueError(f"unsupported group_by: {group_by!r}")
        with self.connection() as conn:
            rows = conn.execute(
                f"SELECT {column} AS k, COUNT(*) AS n FROM reports GROUP BY {column}"
            ).fetchall()
        out: list[dict[str, Any]] = []
        suppressed = 0
        for row in rows:
            n = int(row["n"])
            if n < min_count:
                suppressed += 1
                continue
            out.append({"key": row["k"], "count": n})
        out.sort(key=lambda r: -r["count"])
        return [{"groups": out, "suppressed_cells": suppressed, "min_count": min_count}]

    def stats(self) -> dict[str, Any]:
        with self.connection() as conn:
            reports = conn.execute("SELECT COUNT(*) AS n FROM reports").fetchone()["n"]
            reviewed = conn.execute(
                "SELECT COUNT(DISTINCT report_id) AS n FROM review_actions"
            ).fetchone()["n"]
            audit = conn.execute("SELECT COUNT(*) AS n FROM audit_log").fetchone()["n"]
            results = conn.execute("SELECT COUNT(*) AS n FROM result_records").fetchone()["n"]
            bands = conn.execute(
                "SELECT priority_band AS b, COUNT(*) AS n FROM reports GROUP BY priority_band"
            ).fetchall()
        return {
            "reports": int(reports),
            "reports_reviewed": int(reviewed),
            "reports_pending": int(reports) - int(reviewed),
            "audit_entries": int(audit),
            "result_records": int(results),
            "bands": {r["b"]: int(r["n"]) for r in bands},
        }

    # -- result records ----------------------------------------------------------------

    def insert_result_records(self, records: Sequence[dict[str, Any]]) -> int:
        with self._lock, self.transaction() as conn:
            for rec in records:
                conn.execute(
                    """
                    INSERT INTO result_records (
                        id, pu_id, registered_voters, accredited_voters, rejected_votes,
                        votes_json, report_json, content_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rec["id"],
                        rec["pu_id"],
                        rec["registered_voters"],
                        rec["accredited_voters"],
                        rec["rejected_votes"],
                        json.dumps(rec["votes"], sort_keys=True),
                        json.dumps(rec["rule_report"], ensure_ascii=False),
                        rec["content_hash"],
                        rec["created_at"],
                    ),
                )
        return len(records)

    def list_result_records(self, only_flagged: bool = False, limit: int = 500) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM result_records ORDER BY pu_id ASC LIMIT ?", (limit,)
            ).fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["votes"] = json.loads(item.pop("votes_json"))
            item["rule_report"] = json.loads(item.pop("report_json"))
            if only_flagged and not item["rule_report"]["findings"]:
                continue
            out.append(item)
        return out

    def get_result_record(self, pu_id: str) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM result_records WHERE pu_id = ? ORDER BY created_at DESC LIMIT 1",
                (pu_id,),
            ).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["votes"] = json.loads(item.pop("votes_json"))
        item["rule_report"] = json.loads(item.pop("report_json"))
        return item
