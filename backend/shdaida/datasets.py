"""Loaders for the official synthetic starter pack.

The pack is the organisers' own fictional data (`data/synthetic/` in the hackathon
repository). Using it means our evaluation numbers are directly comparable to the injected
ground truth the organisers published, rather than to a metric we invented.

Nothing here loads personal data, because the pack contains none: party labels are abstract
letters, polling-unit IDs are ``SIM-#####``, and every claim carries the note
"Fully synthetic; not a real claim."
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from .assist import ArchiveClaim
from .rules import ResultRecord


@dataclass(frozen=True)
class IncidentRow:
    incident_id: str
    timestamp: str
    state: str
    lga: str
    pu_id: str
    category: str
    description: str
    severity: int
    reporter_type: str
    verified: bool
    has_photo_evidence: bool


def _as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def load_results(path: Path) -> list[ResultRecord]:
    """Load ``results_synthetic.csv`` into :class:`ResultRecord` objects."""
    records: list[ResultRecord] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            votes = {
                key.removeprefix("votes_"): int(row[key])
                for key in row
                if key.startswith("votes_") and row[key] not in ("", None)
            }
            records.append(
                ResultRecord(
                    pu_id=row["pu_id"],
                    registered_voters=int(row["registered_voters"]),
                    accredited_voters=int(row["accredited_voters"]),
                    votes=votes,
                    rejected_votes=int(row["rejected_votes"]),
                )
            )
    return records


def load_anomaly_labels(path: Path) -> dict[str, str]:
    """Load the organisers' held-out answer key: pu_id -> anomaly_type."""
    labels: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            labels[row["pu_id"]] = row["anomaly_type"]
    return labels


def load_incidents(path: Path) -> list[IncidentRow]:
    rows: list[IncidentRow] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                IncidentRow(
                    incident_id=row["incident_id"],
                    timestamp=row["timestamp"],
                    state=row["state"],
                    lga=row["lga"],
                    pu_id=row["pu_id"],
                    category=row["category"],
                    description=row["description"],
                    severity=int(row["severity_0_4"]),
                    reporter_type=row["reporter_type"],
                    verified=_as_bool(row["verified"]),
                    has_photo_evidence=_as_bool(row["has_photo_evidence"]),
                )
            )
    return rows


def load_claims(path: Path) -> list[ArchiveClaim]:
    """Load ``misinformation_claims_synthetic.jsonl`` as an archive.

    The pack's own ``label`` field is retained as the *archive's* prior assessment, and is
    surfaced to a human as "what a reviewer concluded before", never as SHAIDA's verdict.
    """
    claims: list[ArchiveClaim] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            claims.append(
                ArchiveClaim(
                    claim_id=row["claim_id"],
                    text=row["text"],
                    label=row.get("label", "unverifiable"),
                    language=row.get("language", "en"),
                    channel=row.get("channel", "unknown"),
                    verdict_summary=row.get("note", ""),
                )
            )
    return claims


def load_polling_units(path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            out[row["pu_id"]] = dict(row)
    return out


def load_faq(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def iter_claims_texts(path: Path) -> Iterator[str]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)["text"]
