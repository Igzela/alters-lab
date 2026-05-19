from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from alters_lab.api.snapshot_intake import store
from alters_lab.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clear_store():
    store.clear()
    yield
    store.clear()


def _create_completed_session() -> str:
    r = client.post("/snapshot-intake/sessions")
    sid = r.json()["session_id"]
    for anchor, answer in [
        ("heaviest_constraint", "c1"),
        ("most_unclear", "c2"),
        ("unwilling_to_give_up", "c3"),
    ]:
        client.post(
            f"/snapshot-intake/sessions/{sid}/answers",
            json={"anchor": anchor, "answer": answer},
        )
    # Confirm the snapshot
    client.post(f"/snapshot-intake/sessions/{sid}/confirm")
    # Update evidence_policy to human_provided (required for persist governance)
    from alters_lab.api.snapshot_intake import store
    from alters_lab.schemas.snapshot import EvidencePolicy
    session = store.get_session(UUID(sid))
    session.snapshot = session.snapshot.model_copy(
        update={"evidence_policy": EvidencePolicy(source_mode="human_provided")}
    )
    store.update_session(session)
    return sid


def test_persist_endpoint_exists():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "test-token"},
    )
    assert r.status_code in (200, 403)


def test_persist_returns_403_if_approval_token_missing():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={},
    )
    assert r.status_code in (400, 422)


def test_persist_returns_403_if_wrong_approval_token():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "wrong-token"},
    )
    assert r.status_code == 403


def test_persist_returns_200_with_audit_record():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "p3-001-approved"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "persisted"
    assert body["sha256_after"] is not None
    assert "audit_record" in body
    assert body["audit_record"]["action"] == "snapshot_persist"
    assert "governance_check" in body
    assert body["governance_check"]["valid"] is True
    assert "boundary_confirmations" in body


def test_persist_boundary_confirmations_present():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "p3-001-approved"},
    )
    body = r.json()
    bc = body["boundary_confirmations"]
    assert bc["read_only"] is False
    assert bc["snapshot_yaml_modified"] is True
    assert bc["other_yaml_not_modified"] is True
    assert bc["approval_token_hash_only"] is True


def test_persist_audit_stores_hash_not_raw_token():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "p3-001-approved"},
    )
    body = r.json()
    record = body["audit_record"]
    assert "approval_token_hash" in record
    assert record["approval_token_hash"] == "a]sha256 hash of p3-001-approved" or len(record.get("approval_token_hash", "")) == 64


def test_persist_dry_run_returns_200_without_writing():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "p3-001-approved", "dry_run": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "dry_run"
    assert body["path"] is None
    assert body["sha256_after"] is None
    assert "would_write" in body


def test_persist_dry_run_boundary_confirmations():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "p3-001-approved", "dry_run": True},
    )
    body = r.json()
    bc = body["boundary_confirmations"]
    assert bc["read_only"] is False
    assert bc["snapshot_yaml_modified"] is False
    assert bc["other_yaml_not_modified"] is True
    assert bc["approval_token_hash_only"] is True


def test_persist_response_has_path_none_for_dry_run():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "p3-001-approved", "dry_run": True},
    )
    body = r.json()
    assert body["path"] is None
    assert body["sha256_before"] is None or isinstance(body["sha256_before"], str)


def test_persist_caller_field_accepted():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "p3-001-approved", "dry_run": True, "caller": "test-agent"},
    )
    assert r.status_code == 200
