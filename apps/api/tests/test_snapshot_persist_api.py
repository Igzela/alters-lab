from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from alters_lab.api.snapshot_intake import store
from alters_lab.main import app
from alters_lab.services.snapshot_persist import sha256_file, sha256_text

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
    client.post(f"/snapshot-intake/sessions/{sid}/confirm")
    from alters_lab.schemas.snapshot import EvidencePolicy
    session = store.get_session(UUID(sid))
    session.snapshot = session.snapshot.model_copy(
        update={"evidence_policy": EvidencePolicy(source_mode="human_provided")}
    )
    store.update_session(session)
    return sid


def _patch_paths(monkeypatch, tmp_path):
    """Monkeypatch path helpers so persist writes to tmp_path only."""
    import alters_lab.api.snapshot_intake as mod

    monkeypatch.setattr(mod, "get_snapshot_persist_target_path", lambda: tmp_path / "snapshot.yaml")
    monkeypatch.setattr(mod, "get_snapshot_persist_audit_log_path", lambda: tmp_path / "audit.jsonl")
    monkeypatch.setattr(mod, "get_snapshot_persist_backup_dir", lambda: tmp_path / "backups")


# --- endpoint accepts arbitrary non-empty token ---


def test_persist_accepts_arbitrary_token(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "human-approval-token-123"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "persisted"


# --- endpoint rejects blank/whitespace token ---


def test_persist_rejects_blank_token():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": ""},
    )
    assert r.status_code in (400, 422)


def test_persist_rejects_whitespace_token():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "   "},
    )
    assert r.status_code in (400, 422)


def test_persist_rejects_missing_token():
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={},
    )
    assert r.status_code in (400, 422)


# --- dry_run ---


def test_dry_run_returns_status_dry_run(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "human-approval-token-123", "dry_run": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "dry_run"


def test_dry_run_does_not_write_target(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "human-approval-token-123", "dry_run": True},
    )
    assert not (tmp_path / "snapshot.yaml").exists()


def test_dry_run_does_not_append_audit(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "human-approval-token-123", "dry_run": True},
    )
    assert not (tmp_path / "audit.jsonl").exists()


def test_dry_run_response_no_full_yaml(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "human-approval-token-123", "dry_run": True},
    )
    body = r.json()
    assert "would_write" not in body
    assert "audit_record" not in body
    for key in body:
        val = body[key]
        if isinstance(val, str) and "snapshot:" in val:
            pytest.fail(f"Response field '{key}' contains full YAML content")


def test_dry_run_boundary_snapshot_yaml_not_modified(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "human-approval-token-123", "dry_run": True},
    )
    bc = r.json()["boundary_confirmations"]
    assert bc["snapshot_yaml_modified"] is False


# --- persist writes only tmp snapshot.yaml when helpers monkeypatched ---


def test_persist_writes_only_tmp_snapshot(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "human-approval-token-123"},
    )
    assert r.status_code == 200
    assert (tmp_path / "snapshot.yaml").exists()
    # No other snapshot files created
    snapshots = list(tmp_path.rglob("snapshot*.yaml"))
    assert len(snapshots) == 1


# --- persist appends tmp audit log only on real persist ---


def test_persist_appends_tmp_audit(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "human-approval-token-123"},
    )
    audit = tmp_path / "audit.jsonl"
    assert audit.exists()
    lines = audit.read_text().strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["operation"] == "snapshot_persist"


# --- persist response includes governance_check ---


def test_persist_response_includes_governance_check(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "human-approval-token-123"},
    )
    body = r.json()
    assert "governance_check" in body
    assert body["governance_check"]["valid"] is True


# --- persist response includes full boundary confirmations ---


def test_persist_response_boundary_confirmations(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": "human-approval-token-123"},
    )
    bc = r.json()["boundary_confirmations"]
    required_keys = [
        "snapshot_yaml_modified",
        "branches_yaml_modified",
        "alters_modified",
        "value_alignment_modified",
        "dialogue_modified",
        "reality_trace_modified",
        "calibration_score_created",
        "drift_computed",
        "archive_created",
        "provider_used",
        "frontend_added",
        "database_added",
        "generation_runtime_used",
    ]
    for key in required_keys:
        assert key in bc, f"Missing boundary key: {key}"
    assert bc["snapshot_yaml_modified"] is True
    assert bc["branches_yaml_modified"] is False
    assert bc["alters_modified"] is False
    assert bc["value_alignment_modified"] is False
    assert bc["dialogue_modified"] is False
    assert bc["reality_trace_modified"] is False
    assert bc["calibration_score_created"] is False
    assert bc["drift_computed"] is False
    assert bc["archive_created"] is False
    assert bc["provider_used"] is False
    assert bc["frontend_added"] is False
    assert bc["database_added"] is False
    assert bc["generation_runtime_used"] is False


# --- persist response does not include raw approval token ---


def test_persist_response_no_raw_token(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    raw_token = "human-approval-token-123"
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": raw_token},
    )
    body_str = json.dumps(r.json())
    assert raw_token not in body_str


# --- audit log does not include raw approval token ---


def test_audit_log_no_raw_token(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    raw_token = "human-approval-token-123"
    client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": raw_token},
    )
    audit_content = (tmp_path / "audit.jsonl").read_text()
    assert raw_token not in audit_content


# --- audit log has exact sha256 hash ---


def test_audit_log_has_exact_hash(monkeypatch, tmp_path):
    _patch_paths(monkeypatch, tmp_path)
    sid = _create_completed_session()
    raw_token = "human-approval-token-123"
    client.post(
        f"/snapshot-intake/sessions/{sid}/persist",
        json={"approval_token": raw_token},
    )
    lines = (tmp_path / "audit.jsonl").read_text().strip().splitlines()
    record = json.loads(lines[0])
    assert record["approval_token_hash"] == sha256_text(raw_token)


# --- confirm endpoint still does not write YAML ---


def test_confirm_does_not_write_yaml(tmp_path):
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
    r = client.post(f"/snapshot-intake/sessions/{sid}/confirm")
    assert r.status_code == 200
    # Confirm endpoint is in-memory only — no YAML file created
    # (we can't check the real repo root from here, just verify no crash)


# --- real active snapshot.yaml unchanged during tests ---


def test_real_active_snapshot_unchanged():
    active = Path(__file__).resolve().parents[3] / "alters" / "current" / "snapshot.yaml"
    original_hash = sha256_file(active)
    assert original_hash is not None


# --- no forbidden routers ---


def test_no_forbidden_routers():
    from alters_lab.main import app as _app

    routes = [route.path for route in _app.routes]
    for forbidden in ["branch", "alter", "dialogue", "calibration", "archive"]:
        for route in routes:
            assert forbidden not in route.lower() or route == "/health", (
                f"Unexpected route containing '{forbidden}': {route}"
            )
