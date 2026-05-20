"""API tests for draft review and promotion boundary."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def _valid_draft_package() -> dict:
    return {
        "draft_id": "draft_test_001",
        "status": "draft",
        "active_write_allowed": False,
        "human_review_required": True,
        "generator": {"provider_used": False, "deterministic": True, "mode": "draft_only", "version": "1.0"},
        "boundary_confirmations": {"draft_only": True, "active_yaml_modified": False},
        "branch_drafts": [
            {"id": f"branch_{c}", "label": f"Branch {c}", "draft_status": "candidate", "requires_human_review": True,
             "core_choice": "x", "structural_commitment": "x", "key_tension_resolved": "x",
             "incompatible_with": [f"branch_{x}" for x in "ABCD" if x != c], "source_reasoning": ["reason"]}
            for c in "ABCD"
        ],
        "alter_drafts": [
            {"id": f"alter_{c}", "branch_ref": f"branch_{c}", "label": f"Alter {c}",
             "draft_status": "candidate", "requires_human_review": True,
             "quality_status": {"human_confirmed": False, "active": False},
             "source_refs": {"snapshot_ref": "alters/current/snapshot.yaml", "branches_ref": "alters/current/branches.yaml", "rubric_ref": "alters/calibration/rubric.yaml"}, "voice": {"core_stance": "focused"}}
            for c in "ABCD"
        ],
    }


def _write_draft(workspace: Path, draft_id: str, pkg: dict):
    d = workspace / draft_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "draft_package.yaml").write_text(yaml.dump(pkg), encoding="utf-8")


def _patch_workspace(monkeypatch, tmp_path):
    import alters_lab.api.draft_review as mod
    monkeypatch.setattr(mod, "get_draft_review_workspace", lambda: tmp_path / "drafts")


# --- health ---


def test_draft_review_health():
    r = client.get("/draft-review/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["component"] == "draft-review"
    assert body["mode"] == "review_boundary"
    assert body["active_write_allowed"] is False
    assert body["provider_used"] is False


# --- review endpoint ---


def test_review_missing_draft_returns_404(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.post("/draft-review/nonexistent/review", json={
        "decision": "reject", "notes": ["missing"],
    })
    assert r.status_code == 404


def test_review_path_traversal_rejected(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.post("/draft-review/../etc/passwd/review", json={
        "decision": "reject", "notes": ["hack"],
    })
    assert r.status_code in (400, 404, 422)


def test_review_preview_mode_writes_nothing(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_draft(tmp_path / "drafts", "draft_001", _valid_draft_package())
    r = client.post("/draft-review/draft_001/review", json={
        "decision": "reject", "notes": ["fix"], "save_review": False,
    })
    assert r.status_code == 200
    assert r.json()["status"] == "reviewed"
    assert r.json()["review_path"] is None
    assert not (tmp_path / "drafts" / "draft_001" / "review_decision.yaml").exists()


def test_review_approve_returns_promotion_package(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_draft(tmp_path / "drafts", "draft_001", _valid_draft_package())
    r = client.post("/draft-review/draft_001/review", json={
        "decision": "approve_for_promotion_package",
        "approved_branch_ids": ["branch_A", "branch_B", "branch_C", "branch_D"],
        "approved_alter_ids": ["alter_A", "alter_B", "alter_C", "alter_D"],
    })
    assert r.status_code == 200
    body = r.json()
    assert body["promotion_package"] is not None
    assert body["promotion_package"]["active_write_allowed"] is False
    assert body["promotion_package"]["requires_controlled_persist_api"] is True
    assert "/branches/persist" in body["promotion_package"]["target_persist_apis"]
    assert "/alters/persist-batch" in body["promotion_package"]["target_persist_apis"]


def test_review_save_writes_files(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_draft(tmp_path / "drafts", "draft_001", _valid_draft_package())
    r = client.post("/draft-review/draft_001/review", json={
        "decision": "reject", "notes": ["fix"], "save_review": True, "approval_token": "tok",
    })
    assert r.status_code == 200
    assert r.json()["status"] == "review_saved"
    assert (tmp_path / "drafts" / "draft_001" / "review_decision.yaml").exists()


def test_review_save_requires_token(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_draft(tmp_path / "drafts", "draft_001", _valid_draft_package())
    r = client.post("/draft-review/draft_001/review", json={
        "decision": "reject", "notes": ["fix"], "save_review": True,
    })
    assert r.status_code == 400


def test_review_no_active_yaml_written(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_draft(tmp_path / "drafts", "draft_001", _valid_draft_package())
    client.post("/draft-review/draft_001/review", json={
        "decision": "approve_for_promotion_package",
        "approved_branch_ids": ["branch_A", "branch_B", "branch_C", "branch_D"],
        "approved_alter_ids": ["alter_A", "alter_B", "alter_C", "alter_D"],
        "save_review": True, "approval_token": "tok",
    })
    assert not (tmp_path / "alters").exists()


def test_review_no_raw_token_in_response(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_draft(tmp_path / "drafts", "draft_001", _valid_draft_package())
    r = client.post("/draft-review/draft_001/review", json={
        "decision": "reject", "notes": ["fix"], "save_review": True, "approval_token": "secret",
    })
    body_str = str(r.json())
    assert "secret" not in body_str


# --- list ---


def test_list_returns_empty(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.get("/draft-review/list")
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_list_returns_metadata_only(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_draft(tmp_path / "drafts", "draft_001", _valid_draft_package())
    r = client.get("/draft-review/list")
    assert r.json()["count"] == 1
    assert "branch_A" not in str(r.json())


# --- extra field rejection ---


def test_review_rejects_extra_fields():
    r = client.post("/draft-review/draft_001/review", json={
        "decision": "reject", "provider": {"name": "openai"},
    })
    assert r.status_code == 422


def test_review_rejects_calibration():
    r = client.post("/draft-review/draft_001/review", json={
        "decision": "reject", "calibration": {"score": 0.9},
    })
    assert r.status_code == 422


# --- no forbidden routers ---


def test_no_forbidden_routers():
    from alters_lab.main import app as _app
    routes = [route.path for route in _app.routes]
    for forbidden in ["dialogue", "calibration", "archive"]:
        for route in routes:
            if forbidden in route.lower() and route != "/health" and not route.startswith("/alter-dialogue") and not route.startswith("/calibration-loop") and not route.startswith("/archive-mechanism") and not route.startswith("/provider-dialogue"):
                pytest.fail(f"Unexpected route: {route}")


# --- no provider imports ---


def test_no_provider_imports():
    import ast
    from pathlib import Path
    api_dir = Path(__file__).resolve().parent.parent / "src" / "alters_lab" / "api"
    for py_file in api_dir.glob("draft_review.py"):
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", None) or ""
                names = [a.name for a in getattr(node, "names", [])]
                for forbidden in ["openai", "anthropic", "openrouter", "litellm", "langchain", "crewai"]:
                    if forbidden in mod or any(forbidden in n for n in names):
                        pytest.fail(f"Provider import found: {forbidden}")


# --- no persist API calls ---


def test_no_persist_api_calls():
    import ast
    from pathlib import Path
    service_file = Path(__file__).resolve().parent.parent / "src" / "alters_lab" / "services" / "draft_review.py"
    tree = ast.parse(service_file.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                if func.attr in ("write_branches_with_audit", "write_alter_with_audit", "write_alter_batch_with_audit"):
                    pytest.fail(f"Persist API call found: {func.attr}")
