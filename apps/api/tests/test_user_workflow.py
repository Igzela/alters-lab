"""Tests for P5-M6 User Workflow Integration service."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.user_workflow import (
    UserWorkflowStateResponse,
    WorkflowRunSummaryRequest,
    WorkflowRunSummaryResponse,
)
from alters_lab.services.user_workflow import (
    get_user_workflow_health,
    get_user_workflow_state,
    save_workflow_run_summary,
)


def test_health_response():
    r = get_user_workflow_health()
    assert r.status == "ok"
    assert r.component == "user-workflow"
    assert r.read_only is True


def test_state_endpoint(tmp_path):
    r = get_user_workflow_state(tmp_path)
    assert isinstance(r, UserWorkflowStateResponse)
    assert r.read_only is True
    assert isinstance(r.available_alters, list)
    assert r.provider_status == "mock_default"
    assert isinstance(r.last_reality_scores, list)


def test_state_no_provider_call(tmp_path):
    r = get_user_workflow_state(tmp_path)
    assert r.provider_status == "mock_default"


def test_save_summary_writes_only_tmp(tmp_path):
    req = WorkflowRunSummaryRequest(action="test_action", alter_id="alter_A", notes="test")
    resp = save_workflow_run_summary(req, tmp_path)
    assert isinstance(resp, WorkflowRunSummaryResponse)
    assert resp.status == "saved"
    assert resp.run_id is not None
    assert resp.run_path is not None
    assert "alters/product/workflow_runs" in resp.run_path
    assert resp.active_yaml_modified is False


def test_no_active_yaml_diff(tmp_path):
    req = WorkflowRunSummaryRequest(action="test", alter_id="alter_A")
    save_workflow_run_summary(req, tmp_path)
    assert not (tmp_path / "alters" / "current").exists()


def test_no_secrets(tmp_path):
    req = WorkflowRunSummaryRequest(action="test", alter_id="alter_A")
    resp = save_workflow_run_summary(req, tmp_path)
    run_path = Path(resp.run_path)
    if run_path.exists():
        content = run_path.read_text()
        assert "sk-" not in content.lower()
        assert "api_key" not in content.lower()
