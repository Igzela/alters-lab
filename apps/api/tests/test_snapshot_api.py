from __future__ import annotations

import os
from pathlib import Path

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


# --- Health ---


def test_root_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_snapshot_intake_health():
    r = client.get("/snapshot-intake/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["component"] == "snapshot-intake"


# --- Session creation ---


def test_create_session_returns_201():
    r = client.post("/snapshot-intake/sessions")
    assert r.status_code == 201
    body = r.json()
    assert "session_id" in body
    assert body["snapshot"]["intake_status"]["pending_anchor"] == "heaviest_constraint"


def test_created_session_starts_at_heaviest_constraint():
    r = client.post("/snapshot-intake/sessions")
    body = r.json()
    assert body["snapshot"]["intake_status"]["phase"] == "asking_heaviest_constraint"
    assert body["snapshot"]["intake_status"]["pending_anchor"] == "heaviest_constraint"


def test_get_session_returns_same_session():
    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
    r = client.get(f"/snapshot-intake/sessions/{sid}")
    assert r.status_code == 200
    assert r.json()["session_id"] == sid


def test_get_missing_session_returns_404():
    r = client.get("/snapshot-intake/sessions/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


# --- Next anchor ---


def test_next_anchor_initially_heaviest_constraint():
    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
    r = client.get(f"/snapshot-intake/sessions/{sid}/next-anchor")
    assert r.status_code == 200
    body = r.json()
    assert body["next_anchor"] == "heaviest_constraint"
    assert body["phase"] == "asking_heaviest_constraint"


def test_next_anchor_after_heaviest_returns_most_unclear():
    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
    client.post(
        f"/snapshot-intake/sessions/{sid}/answers",
        json={"anchor": "heaviest_constraint", "answer": "c1"},
    )
    r = client.get(f"/snapshot-intake/sessions/{sid}/next-anchor")
    body = r.json()
    assert body["next_anchor"] == "most_unclear"
    assert body["phase"] == "asking_most_unclear"


def test_next_anchor_after_most_unclear_returns_unwilling():
    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
    client.post(
        f"/snapshot-intake/sessions/{sid}/answers",
        json={"anchor": "heaviest_constraint", "answer": "c1"},
    )
    client.post(
        f"/snapshot-intake/sessions/{sid}/answers",
        json={"anchor": "most_unclear", "answer": "c2"},
    )
    r = client.get(f"/snapshot-intake/sessions/{sid}/next-anchor")
    body = r.json()
    assert body["next_anchor"] == "unwilling_to_give_up"
    assert body["phase"] == "asking_unwilling_to_give_up"


def test_next_anchor_after_all_returns_none_ready():
    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
    for anchor, answer in [
        ("heaviest_constraint", "c1"),
        ("most_unclear", "c2"),
        ("unwilling_to_give_up", "c3"),
    ]:
        client.post(
            f"/snapshot-intake/sessions/{sid}/answers",
            json={"anchor": anchor, "answer": answer},
        )
    r = client.get(f"/snapshot-intake/sessions/{sid}/next-anchor")
    body = r.json()
    assert body["next_anchor"] is None
    assert body["phase"] == "ready_for_snapshot_confirmation"


# --- Answer rules ---


def test_empty_answer_rejected():
    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/answers",
        json={"anchor": "heaviest_constraint", "answer": ""},
    )
    assert r.status_code in (400, 422)


def test_whitespace_only_answer_rejected():
    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/answers",
        json={"anchor": "heaviest_constraint", "answer": "   "},
    )
    assert r.status_code in (400, 422)


def test_unknown_session_rejected():
    r = client.post(
        "/snapshot-intake/sessions/00000000-0000-0000-0000-000000000000/answers",
        json={"anchor": "heaviest_constraint", "answer": "c1"},
    )
    assert r.status_code == 404


def test_out_of_order_answer_rejected():
    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/answers",
        json={"anchor": "most_unclear", "answer": "c2"},
    )
    assert r.status_code == 409


def test_duplicate_answer_rejected():
    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
    client.post(
        f"/snapshot-intake/sessions/{sid}/answers",
        json={"anchor": "heaviest_constraint", "answer": "c1"},
    )
    r = client.post(
        f"/snapshot-intake/sessions/{sid}/answers",
        json={"anchor": "heaviest_constraint", "answer": "c1 again"},
    )
    assert r.status_code == 409


# --- Confirmation ---


def test_confirm_before_all_anchors_rejected():
    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
    client.post(
        f"/snapshot-intake/sessions/{sid}/answers",
        json={"anchor": "heaviest_constraint", "answer": "c1"},
    )
    r = client.post(f"/snapshot-intake/sessions/{sid}/confirm")
    assert r.status_code == 409


def test_confirm_after_all_anchors_succeeds():
    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
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
    body = r.json()
    assert body["snapshot"]["intake_status"]["phase"] == "completed"
    assert body["ready_for_branch_discovery"] is True


def test_confirmed_snapshot_phase_is_completed():
    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
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
    body = r.json()
    assert body["snapshot"]["intake_status"]["phase"] == "completed"
    assert body["snapshot"]["intake_status"]["pending_anchor"] is None


# --- Boundary: no YAML writes ---


def test_confirm_does_not_write_yaml():
    snapshot_yaml = Path("alters/current/snapshot.yaml")
    existed_before = snapshot_yaml.exists()

    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
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

    if existed_before:
        assert snapshot_yaml.exists()
    else:
        assert not snapshot_yaml.exists()


def test_confirm_does_not_create_branch_or_alter_files():
    branches_yaml = Path("alters/current/branches.yaml")
    alters_dir = Path("alters/current/alters")

    existed_branches = branches_yaml.exists()
    existed_alters = alters_dir.exists()

    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
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

    if existed_branches:
        assert branches_yaml.exists()
    else:
        assert not branches_yaml.exists()

    if existed_alters:
        assert alters_dir.exists()
    else:
        assert not alters_dir.exists()
