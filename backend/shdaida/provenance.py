"""Cryptographic evidence integrity: content hashing and a tamper-evident hash chain.

This module is deliberately free of any AI. Integrity claims must be deterministic and
reproducible, so a third party can re-derive them without trusting SHAIDA's models.

Design:
  * Every evidence record gets a SHA-256 content hash over a canonical serialisation
    of its fields, so the same record always hashes identically.
  * Records are linked into an append-only chain: each entry commits to the previous
    entry's hash. Removing, reordering or editing an entry breaks every subsequent link,
    which ``verify_chain`` detects and localises.
  * Verification is exposed to users so they can check a record independently.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

# Domain-separation prefix, so a SHAIDA hash can never be confused with a bare SHA-256
# of the same bytes produced by another tool.
_HASH_DOMAIN = b"shaida.v1\0"
_GENESIS = "0" * 64

# Fields that must never influence a content hash, because they are derived or
# mutable metadata rather than evidence content.
_EXCLUDED_FROM_HASH = frozenset(
    {
        "id",
        "content_hash",
        "chain_hash",
        "prev_chain_hash",
        "seq",
        "created_at",
        "chain_index",
    }
)


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    """Canonical serialisation: sorted keys, no insignificant whitespace, UTF-8."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def content_hash(payload: dict[str, Any]) -> str:
    """SHA-256 over the canonical content of a record, excluding derived metadata."""
    material = {k: v for k, v in payload.items() if k not in _EXCLUDED_FROM_HASH}
    digest = hashlib.sha256()
    digest.update(_HASH_DOMAIN)
    digest.update(canonical_bytes(material))
    return digest.hexdigest()


def chain_hash(prev_chain_hash: str, entry_content_hash: str, seq: int) -> str:
    """Hash linking an entry to the whole history that precedes it."""
    digest = hashlib.sha256()
    digest.update(_HASH_DOMAIN)
    digest.update(b"chain\0")
    digest.update(str(seq).encode("ascii"))
    digest.update(b"\0")
    digest.update(prev_chain_hash.encode("ascii"))
    digest.update(b"\0")
    digest.update(entry_content_hash.encode("ascii"))
    return digest.hexdigest()


@dataclass(frozen=True)
class ChainEntry:
    seq: int
    content_hash: str
    prev_chain_hash: str
    chain_hash: str


@dataclass(frozen=True)
class ChainVerdict:
    intact: bool
    checked: int
    first_broken_seq: int | None
    reason: str | None


def build_chain(entries: Iterable[tuple[int, str]]) -> list[ChainEntry]:
    """Build a chain from ``(seq, content_hash)`` pairs in order."""
    out: list[ChainEntry] = []
    prev = _GENESIS
    for seq, chash in entries:
        link = chain_hash(prev, chash, seq)
        out.append(ChainEntry(seq=seq, content_hash=chash, prev_chain_hash=prev, chain_hash=link))
        prev = link
    return out


def verify_chain(chain: Sequence[ChainEntry]) -> ChainVerdict:
    """Recompute a chain from scratch and report the first inconsistency.

    Checks performed, in order, for each entry:
      1. sequence numbers are strictly increasing by one (detects deletion/reordering);
      2. the stored previous link equals the recomputed previous link (detects splicing);
      3. the recomputed link equals the stored link (detects edits).
    """
    prev = _GENESIS
    expected_seq = chain[0].seq if chain else 0
    for index, entry in enumerate(chain):
        if entry.seq != expected_seq:
            return ChainVerdict(
                intact=False,
                checked=index,
                first_broken_seq=entry.seq,
                reason=(
                    f"sequence gap at position {index}: expected {expected_seq}, "
                    f"found {entry.seq} (entries may have been deleted or reordered)"
                ),
            )
        if entry.prev_chain_hash != prev:
            return ChainVerdict(
                intact=False,
                checked=index,
                first_broken_seq=entry.seq,
                reason=f"broken link at seq {entry.seq}: previous-link mismatch",
            )
        recomputed = chain_hash(prev, entry.content_hash, entry.seq)
        if recomputed != entry.chain_hash:
            return ChainVerdict(
                intact=False,
                checked=index,
                first_broken_seq=entry.seq,
                reason=f"tampered entry at seq {entry.seq}: link hash does not recompute",
            )
        prev = entry.chain_hash
        expected_seq += 1
    return ChainVerdict(intact=True, checked=len(chain), first_broken_seq=None, reason=None)


def verify_record(payload: dict[str, Any], claimed_hash: str) -> bool:
    """Independently verify a single record against a claimed content hash."""
    if not isinstance(claimed_hash, str) or len(claimed_hash) != 64:
        return False
    return content_hash(payload) == claimed_hash
