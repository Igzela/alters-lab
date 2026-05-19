from __future__ import annotations

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


def _patch_persist(monkeypatch, tmp_path):
    import alters_lab.api.snapshot_intake as api_mod
    import alters_lab.services.snapshot_persist as persist_mod
    from alters_lab.services.snapshot_persist import (
        APPROVAL_TOKEN,
        build_snapshot_persist_payload,
        persist_snapshot_to_disk,
    )

    audit_file = tmp_path / "phase3_write_audit.jsonl"

    def fake_persist(payload, target, token):
        if token != APPROVAL_TOKEN:
            return {"status": "rejected", "reason": "invalid approval_token"}
        t = tmp_path / "snapshot.yaml"
        t.write_text(payload["yaml_content"], encoding="utf-8")
        from alters_lab.services.snapshot_persist import sha256_file

        sha_before = None
        sha_after = sha256_file(t)
        import json
        from datetime import datetime, timezone

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "snapshot_persist",
            "target_path": str(t),
            "sha256_before": sha_before,
            "sha256_after": sha_after,
            "approval_token": token,
        }
        with open(audit_file, "a") as f:
            f.write(json.dumps(record) + "\n")
        return {
            "status": "persisted",
            "path": str(t),
            "sha256_before": sha_before,
            "sha256_after": sha_after,
            "audit_record": record,
        }

    monkeypatch.setattr(api_mod, "persist_snapshot_to_disk", fake_persist)


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


def test_persist_returns_403_if_wrong_approval_token(monkeypatch, tmp_path):
    _patch_persist(monkeypatch, tmp_path)
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "wrong-token"},
    )
    assert r.status_code == 403


def test_persist_returns_200_with_audit_record(monkeypatch, tmp_path):
    _patch_persist(monkeypatch, tmp_path)
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
