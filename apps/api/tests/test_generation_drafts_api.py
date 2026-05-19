"""API tests for generation draft runtime."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def _patch_draft_paths(monkeypatch, tmp_path):
    import alters_lab.api.generation_drafts as mod
    monkeypatch.setattr(mod, "get_generation_draft_workspace", lambda: tmp_path / "drafts")
    monkeypatch.setattr(mod, "get_generation_draft_audit_log_path", lambda: tmp_path / "audit.jsonl")


def _patch_loader(monkeypatch):
    import alters_lab.api.generation_drafts as mod

    def _fake_load():
        return {
            "snapshot": {"intake_status": {"phase": "completed"}},
            "branches": {"branches": [
                {"id": "branch_A"}, {"id": "branch_B"},
                {"id": "branch_C"}, {"id": "branch_D"},
            ]},
        }

    monkeypatch.setattr(mod, "load_active_yaml_chain", _fake_load)


# --- health ---


def test_generation_drafts_health():
    r = client.get("/generation-drafts/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["component"] == "generation-drafts"
    assert body["mode"] == "draft_only"
    assert body["provider_used"] is False


# --- preview (no save) ---


def test_preview_returns_draft_generated(monkeypatch, tmp_path):
    _patch_draft_paths(monkeypatch, tmp_path)
    _patch_loader(monkeypatch)
    r = client.post("/generation-drafts/preview", json={
        "save_draft": False,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "draft_generated"
    assert body["draft_package"]["active_write_allowed"] is False
    assert body["draft_package"]["human_review_required"] is True
    assert body["draft_package"]["generator"]["provider_used"] is False


def test_preview_does_not_create_files(monkeypatch, tmp_path):
    _patch_draft_paths(monkeypatch, tmp_path)
    _patch_loader(monkeypatch)
    client.post("/generation-drafts/preview", json={"save_draft": False})
    assert not (tmp_path / "drafts").exists()


def test_preview_includes_boundary_confirmations(monkeypatch, tmp_path):
    _patch_draft_paths(monkeypatch, tmp_path)
    _patch_loader(monkeypatch)
    r = client.post("/generation-drafts/preview", json={"save_draft": False})
    bc = r.json()["boundary_confirmations"]
    assert bc["draft_only"] is True
    assert bc["provider_used"] is False
    assert bc["active_yaml_modified"] is False


def test_preview_branch_drafts(monkeypatch, tmp_path):
    _patch_draft_paths(monkeypatch, tmp_path)
    _patch_loader(monkeypatch)
    r = client.post("/generation-drafts/preview", json={
        "include_branches": True, "include_alters": False, "save_draft": False,
    })
    pkg = r.json()["draft_package"]
    assert len(pkg["branch_drafts"]) == 4
    assert len(pkg["alter_drafts"]) == 0


def test_preview_alter_drafts(monkeypatch, tmp_path):
    _patch_draft_paths(monkeypatch, tmp_path)
    _patch_loader(monkeypatch)
    r = client.post("/generation-drafts/preview", json={
        "include_branches": False, "include_alters": True, "save_draft": False,
    })
    pkg = r.json()["draft_package"]
    assert len(pkg["branch_drafts"]) == 0
    assert len(pkg["alter_drafts"]) == 4


# --- preview with save ---


def test_save_draft_requires_token(monkeypatch, tmp_path):
    _patch_draft_paths(monkeypatch, tmp_path)
    _patch_loader(monkeypatch)
    r = client.post("/generation-drafts/preview", json={"save_draft": True})
    assert r.status_code in (400, 422)


def test_save_draft_writes_only_draft_workspace(monkeypatch, tmp_path):
    _patch_draft_paths(monkeypatch, tmp_path)
    _patch_loader(monkeypatch)
    r = client.post("/generation-drafts/preview", json={
        "save_draft": True, "approval_token": "test-token",
    })
    assert r.status_code == 200
    assert r.json()["status"] == "draft_saved"
    assert r.json()["draft_path"] is not None
    drafts_dir = tmp_path / "drafts"
    assert drafts_dir.exists()


def test_save_draft_appends_audit(monkeypatch, tmp_path):
    _patch_draft_paths(monkeypatch, tmp_path)
    _patch_loader(monkeypatch)
    client.post("/generation-drafts/preview", json={
        "save_draft": True, "approval_token": "test-token",
    })
    audit = tmp_path / "audit.jsonl"
    assert audit.exists()
    lines = audit.read_text().strip().splitlines()
    record = json.loads(lines[0])
    assert record["operation"] == "generation_draft_save"


def test_save_draft_no_raw_token(monkeypatch, tmp_path):
    _patch_draft_paths(monkeypatch, tmp_path)
    _patch_loader(monkeypatch)
    raw_token = "human-approval-token-123"
    client.post("/generation-drafts/preview", json={
        "save_draft": True, "approval_token": raw_token,
    })
    content = (tmp_path / "audit.jsonl").read_text()
    assert raw_token not in content


# --- list ---


def test_list_returns_empty(monkeypatch, tmp_path):
    _patch_draft_paths(monkeypatch, tmp_path)
    r = client.get("/generation-drafts/list")
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_list_after_save(monkeypatch, tmp_path):
    _patch_draft_paths(monkeypatch, tmp_path)
    _patch_loader(monkeypatch)
    client.post("/generation-drafts/preview", json={
        "save_draft": True, "approval_token": "test-token",
    })
    r = client.get("/generation-drafts/list")
    assert r.json()["count"] == 1


# --- extra field rejection ---


def test_preview_rejects_extra_fields():
    r = client.post("/generation-drafts/preview", json={
        "provider": {"name": "openai"},
    })
    assert r.status_code == 422


def test_preview_rejects_calibration():
    r = client.post("/generation-drafts/preview", json={
        "calibration": {"score": 0.9},
    })
    assert r.status_code == 422


# --- active YAML unchanged ---


def test_active_yaml_unchanged_after_preview(monkeypatch, tmp_path):
    _patch_draft_paths(monkeypatch, tmp_path)
    _patch_loader(monkeypatch)
    client.post("/generation-drafts/preview", json={"save_draft": False})
    assert not (tmp_path / "drafts").exists()


# --- no forbidden routers ---


def test_no_forbidden_routers():
    from alters_lab.main import app as _app
    routes = [route.path for route in _app.routes]
    for forbidden in ["dialogue", "calibration", "archive"]:
        for route in routes:
            if forbidden in route.lower() and route != "/health":
                pytest.fail(f"Unexpected route: {route}")


# --- no provider imports ---


def test_no_provider_imports():
    import ast
    from pathlib import Path
    api_dir = Path(__file__).resolve().parent.parent / "src" / "alters_lab" / "api"
    for py_file in api_dir.glob("generation_drafts.py"):
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", None) or ""
                names = [a.name for a in getattr(node, "names", [])]
                for forbidden in ["openai", "anthropic", "openrouter", "litellm", "langchain", "crewai"]:
                    if forbidden in mod or any(forbidden in n for n in names):
                        pytest.fail(f"Provider import found: {forbidden}")


# --- real loader integration ---


def test_preview_with_real_loader_no_monkeypatch(monkeypatch, tmp_path):
    """POST /generation-drafts/preview works with real load_active_yaml_chain."""
    _patch_draft_paths(monkeypatch, tmp_path)
    # Do NOT monkeypatch load_active_yaml_chain — use real loader
    r = client.post("/generation-drafts/preview", json={"save_draft": False})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "draft_generated"
    assert len(body["draft_package"]["branch_drafts"]) == 4
    assert len(body["draft_package"]["alter_drafts"]) == 4


def test_preview_real_loader_real_wrapped_snapshot(monkeypatch, tmp_path):
    """Real loader returns ActiveYamlChain with wrapped snapshot shape."""
    _patch_draft_paths(monkeypatch, tmp_path)
    # Load real chain to verify it passes validation
    from alters_lab.loaders.active_yaml import load_active_yaml_chain
    chain = load_active_yaml_chain()
    # Verify real shape: snapshot is wrapped
    assert "snapshot" in chain.snapshot
    assert "intake_status" in chain.snapshot["snapshot"]
    # Verify branches has real branch list
    branch_list = chain.branches.get("branches", [])
    assert len(branch_list) == 4
    branch_ids = {b["id"] for b in branch_list}
    assert branch_ids == {"branch_A", "branch_B", "branch_C", "branch_D"}


def test_preview_validation_failure_returns_400(monkeypatch, tmp_path):
    """Validation failure returns 400 without writing draft or audit."""
    _patch_draft_paths(monkeypatch, tmp_path)
    import alters_lab.api.generation_drafts as mod

    def _broken_load():
        return {
            "snapshot": {"snapshot": {"intake_status": {"phase": "not_started"}}},
            "branches": {"branches": []},
        }

    monkeypatch.setattr(mod, "load_active_yaml_chain", _broken_load)
    r = client.post("/generation-drafts/preview", json={"save_draft": False})
    assert r.status_code == 400
    assert "validation failed" in r.json()["detail"]
    assert not (tmp_path / "drafts").exists()


def test_preview_loader_failure_returns_500(monkeypatch, tmp_path):
    """Loader failure returns 500."""
    _patch_draft_paths(monkeypatch, tmp_path)
    import alters_lab.api.generation_drafts as mod

    def _boom():
        raise RuntimeError("file missing")

    monkeypatch.setattr(mod, "load_active_yaml_chain", _boom)
    r = client.post("/generation-drafts/preview", json={"save_draft": False})
    assert r.status_code == 500
    assert "load failed" in r.json()["detail"]
