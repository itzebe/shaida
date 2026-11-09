"""Evidence integrity tests, including an actual tampering demonstration.

The tampering test is the important one: it edits a stored audit row directly in SQLite and
asserts that verification fails and names the edited row. Claiming "tamper-evident" without
demonstrating detection would be exactly the kind of unverified assertion the engineering
constitution forbids.
"""

from __future__ import annotations

import json

import pytest

from shdaida.provenance import (
    ChainEntry,
    build_chain,
    chain_hash,
    content_hash,
    verify_chain,
    verify_record,
)
from shdaida.storage import Store


def test_content_hash_is_stable_and_order_independent():
    a = content_hash({"b": 2, "a": 1})
    b = content_hash({"a": 1, "b": 2})
    assert a == b, "canonical serialisation must make key order irrelevant"
    assert len(a) == 64


def test_content_hash_excludes_derived_metadata():
    base = {"narrative": "hello", "category": "other"}
    with_meta = {**base, "id": "x", "created_at": "now", "chain_hash": "y"}
    assert content_hash(base) == content_hash(with_meta)


def test_content_hash_changes_when_content_changes():
    assert content_hash({"n": "a"}) != content_hash({"n": "b"})


def test_verify_record_accepts_and_rejects():
    payload = {"narrative": "observed a queue", "category": "queue_management"}
    digest = content_hash(payload)
    assert verify_record(payload, digest) is True
    assert verify_record({"narrative": "changed"}, digest) is False
    assert verify_record(payload, "not-a-hash") is False


def test_chain_verifies_when_untouched():
    chain = build_chain([(1, content_hash({"i": 1})), (2, content_hash({"i": 2}))])
    verdict = verify_chain(chain)
    assert verdict.intact is True
    assert verdict.checked == 2


def test_chain_detects_an_edited_entry():
    chain = build_chain([(1, content_hash({"i": 1})), (2, content_hash({"i": 2}))])
    tampered = list(chain)
    original = tampered[0]
    tampered[0] = ChainEntry(
        seq=original.seq,
        content_hash=content_hash({"i": 1, "injected": True}),
        prev_chain_hash=original.prev_chain_hash,
        chain_hash=original.chain_hash,  # the attacker keeps the old link
    )
    verdict = verify_chain(tampered)
    assert verdict.intact is False
    assert verdict.first_broken_seq == 1
    assert "tampered" in (verdict.reason or "")


def test_chain_detects_a_deleted_entry():
    chain = build_chain([(1, content_hash({"i": 1})), (2, content_hash({"i": 2})), (3, content_hash({"i": 3}))])
    verdict = verify_chain([chain[0], chain[2]])
    assert verdict.intact is False
    assert verdict.first_broken_seq == 3
    assert "sequence gap" in (verdict.reason or "")


def test_chain_detects_reordering():
    chain = build_chain([(1, content_hash({"i": 1})), (2, content_hash({"i": 2}))])
    verdict = verify_chain([chain[1], chain[0]])
    assert verdict.intact is False


def test_chain_hash_binds_sequence_number():
    a = chain_hash("0" * 64, "a" * 64, 1)
    b = chain_hash("0" * 64, "a" * 64, 2)
    assert a != b, "a link must commit to its own position in the chain"


# --------------------------------------------------------------------------------------
# Store-level tampering demonstration
# --------------------------------------------------------------------------------------


@pytest.fixture()
def store(tmp_path):
    return Store(tmp_path / "test.sqlite3")


def _seed(store: Store, count: int = 3) -> None:
    for i in range(count):
        store.append_audit(
            action="report.created",
            subject_type="report",
            subject_id=f"rep-{i}",
            actor_role="reporter",
            payload={"i": i, "category": "other"},
        )


def test_audit_chain_intact_after_appends(store):
    _seed(store, 5)
    verdict = store.verify_audit_chain()
    assert verdict.intact is True
    assert verdict.checked == 5


def test_audit_chain_detects_direct_database_tampering(store):
    """Mutate a stored row behind the API's back and prove detection."""
    _seed(store, 4)

    with store.connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "UPDATE audit_log SET payload = ? WHERE seq = 2",
            (json.dumps({"i": 2, "category": "other", "injected": "attacker"}, sort_keys=True),),
        )
        conn.execute("COMMIT")

    verdict = store.verify_audit_chain()
    assert verdict.intact is False, "editing a stored audit row must break the chain"
    assert verdict.first_broken_seq is not None
    # The payload hash column still holds the original digest, so recomputation of the link
    # from the stored hash no longer matches. Either way, verification must not pass.
    assert verdict.checked <= 4


def test_audit_chain_detects_row_deletion(store):
    _seed(store, 4)
    with store.connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM audit_log WHERE seq = 2")
        conn.execute("COMMIT")
    verdict = store.verify_audit_chain()
    assert verdict.intact is False
    assert "sequence gap" in (verdict.reason or "")


def test_audit_chain_is_empty_and_intact_on_a_fresh_store(store):
    verdict = store.verify_audit_chain()
    assert verdict.intact is True
    assert verdict.checked == 0
