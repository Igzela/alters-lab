"""Tests for P6-M1 Obsidian weekly note ingest API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from alters_lab.main import app
from tests.test_obsidian_weekly_note import VALID_NOTE

client = TestClient(app)


def test_health():
    r = client.get("/obsidian-weekly-note/health")
    assert r.status_code == 200
    data = r.json()
    assert data["component"] == "obsidian-weekly-note"
    assert data["provider_called"] is False


def test_ingest_and_edit(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.services.p6_runtime.get_repo_root", lambda: tmp_path)
    r = client.post("/obsidian-weekly-note/ingest", json={"raw_note": VALID_NOTE, "source_path": "weekly.md"})
    assert r.status_code == 200
    data = r.json()
    record_id = data["record"]["record_id"]
    assert data["record"]["derived_from_raw_note"] is True
    assert "alters/product/weekly_notes" in data["record_path"]

    edit = client.post(f"/obsidian-weekly-note/{record_id}/edit", json={
        "observable_facts": [
            "Completed two focused coding sessions.",
            "Slept before midnight on three nights.",
            "Deferred the provider integration decision.",
            "Wrote down the next correction.",
            "Kept a single review note.",
        ],
        "correction_note": "Corrected extracted facts against raw note.",
    })
    assert edit.status_code == 200
    edited = edit.json()
    assert edited["record"]["raw_note"] == VALID_NOTE
    assert edited["diff"]["challenge_required"] is True


def test_load_missing_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.services.p6_runtime.get_repo_root", lambda: tmp_path)
    r = client.get("/obsidian-weekly-note/missing")
    assert r.status_code == 404


def test_route_inventory():
    routes = sorted(route.path for route in app.routes)
    assert "/obsidian-weekly-note/health" in routes
    assert "/obsidian-weekly-note/ingest" in routes
    assert "/obsidian-weekly-note/{record_id}/edit" in routes
