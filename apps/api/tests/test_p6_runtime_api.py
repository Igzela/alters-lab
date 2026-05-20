"""API tests for P6 code-complete runtime gates."""

from __future__ import annotations

from fastapi.testclient import TestClient

from alters_lab.main import app
from tests.test_obsidian_weekly_note import VALID_NOTE

client = TestClient(app)


def test_p6_route_inventory():
    routes = sorted(route.path for route in app.routes)
    expected = [
        "/weekly-review/health",
        "/action-alignment/health",
        "/self-deception-challenge/health",
        "/alter-recommendation/health",
        "/weekly-reminder/health",
        "/pattern-review/health",
        "/p6-data-retention/health",
        "/p6-provider-policy/health",
        "/behavior-validation/health",
        "/phase6-closeout/health",
    ]
    for route in expected:
        assert route in routes


def test_weekly_review_and_score_flow(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.services.p6_runtime.get_repo_root", lambda: tmp_path)
    note = client.post("/obsidian-weekly-note/ingest", json={"raw_note": VALID_NOTE}).json()["record"]
    started = client.post("/weekly-review/start", json={"weekly_note_record_id": note["record_id"]})
    assert started.status_code == 200
    session_id = started.json()["session"]["session_id"]

    completed = client.post(f"/weekly-review/{session_id}/complete", json={
        "review_note": "Review note.",
        "primary_next_correction": "Pick one primary correction.",
        "supporting_actions": ["Block one review slot."],
    })
    assert completed.status_code == 200
    assert completed.json()["session"]["calibration_record_shell"]["scoring_pending"] is True

    scored = client.post("/action-alignment/score", json={
        "session_id": session_id,
        "scores": {
            "direction_alignment": 0.8,
            "execution_consistency": 0.7,
            "avoidance_level": 0.2,
        },
        "evidence": {
            "one_action_evidence": "Completed two focused coding sessions.",
            "one_avoidance_or_friction_evidence": "Missed one planned review block.",
            "one_next_correction": "Pick one primary correction.",
        },
        "verdict_label": "aligned_progress",
        "verdict_sentence": "Progress was aligned but still somewhat noisy.",
    })
    assert scored.status_code == 200
    assert scored.json()["score"]["derived_from_weekly_review"] is True


def test_provider_policy_and_behavior_gate_api(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.services.p6_runtime.get_repo_root", lambda: tmp_path)
    status = client.get("/p6-provider-policy/status")
    assert status.status_code == 200
    assert status.json()["api_key_returned"] is False

    rejected = client.post("/p6-provider-policy/validate-config", json={
        "mode": "openai_compatible_http",
        "base_url_configured": False,
        "api_key_configured": False,
        "explicit_user_configuration": False,
    })
    assert rejected.status_code == 200
    assert rejected.json()["valid"] is False

    validation = client.post("/behavior-validation/evaluate", json={
        "weekly_review_ids": ["w1", "w2", "w3", "w4"],
        "calibration_record_ids": ["c1", "c2", "c3", "c4"],
        "pattern_review_ids": ["p1"],
        "metrics": {
            "action_alignment_score_improves": True,
            "repeated_negative_patterns_reduce": True,
            "primary_correction_completion_rate_improves": True,
        },
        "usage_integrity": {
            "weekly_notes_completed_honestly": True,
            "calibration_records_created": True,
            "primary_corrections_set": True,
            "failure_reviews_honest": True,
            "self_deception_risk_not_softened": True,
            "sessions_not_skipped_too_often": True,
        },
    })
    assert validation.status_code == 400
    assert "weekly review record not found" in validation.json()["detail"]


def test_retention_archive_and_phase6_closeout_api(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.services.p6_runtime.get_repo_root", lambda: tmp_path)
    note = client.post("/obsidian-weekly-note/ingest", json={"raw_note": VALID_NOTE}).json()["record"]
    archive = client.post("/p6-data-retention/archive", json={
        "records": [{"area": "weekly_notes", "record_id": note["record_id"]}],
        "confirmation": "archive",
    })
    assert archive.status_code == 200
    assert archive.json()["active_yaml_modified"] is False

    closeout = client.get("/phase6-closeout/report")
    assert closeout.status_code == 200
    assert closeout.json()["status"] in ("BLOCKED", "PASS")
