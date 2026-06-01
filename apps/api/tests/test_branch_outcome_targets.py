"""Tests for branch outcome targets schema, service, and API."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from alters_lab.schemas.branch_outcome_targets import (
    BranchOutcomeTargetRecord,
    evaluate_target,
)
from alters_lab.services.branch_outcome_targets import (
    evaluate_existing_target,
    list_targets,
    load_target,
    save_target,
)


@pytest.fixture
def client():
    from alters_lab.main import app
    return TestClient(app)


def _valid_target(**overrides) -> dict:
    base = {
        "branch_id": "branch_A",
        "domain": "career_education",
        "horizon_months": 6,
        "outcome_name": "Ship v1 of project",
        "objective_definition": "Project v1 deployed to production with all core features",
        "success_threshold": "All 5 core features working in production",
        "measurement_method": "Manual deployment verification",
        "baseline_value": "no deployment",
        "target_value": "production deployment",
    }
    base.update(overrides)
    return base


# --- Schema tests ---

def test_cannot_create_without_objective_definition():
    data = _valid_target()
    del data["objective_definition"]
    with pytest.raises(ValidationError, match="objective_definition"):
        BranchOutcomeTargetRecord(**data)


def test_cannot_create_without_success_threshold():
    data = _valid_target()
    del data["success_threshold"]
    with pytest.raises(ValidationError, match="success_threshold"):
        BranchOutcomeTargetRecord(**data)


def test_evaluated_target_records_final_value():
    record = BranchOutcomeTargetRecord(**_valid_target())
    evaluated = evaluate_target(record, "deployed v1 with 5 features", True)
    assert evaluated.final_observed_value == "deployed v1 with 5 features"
    assert evaluated.evaluated_at is not None
    assert evaluated.status == "achieved"


def test_evaluated_target_missed():
    record = BranchOutcomeTargetRecord(**_valid_target())
    evaluated = evaluate_target(record, "only 2 features shipped", False)
    assert evaluated.status == "missed"


def test_valid_target_saves_and_loads(tmp_path: Path):
    record = BranchOutcomeTargetRecord(**_valid_target())
    save_target(record, repo_root=tmp_path)
    loaded = load_target(record.target_id, repo_root=tmp_path)
    assert loaded.target_id == record.target_id
    assert loaded.objective_definition == record.objective_definition


def test_target_id_auto_generated():
    record = BranchOutcomeTargetRecord(**_valid_target())
    assert record.target_id.startswith("bot_")


def test_status_transitions():
    record = BranchOutcomeTargetRecord(**_valid_target())
    assert record.status == "planned"
    assert record.can_transition_to("active")
    assert record.can_transition_to("abandoned")
    assert not record.can_transition_to("achieved")  # can't go directly from planned to achieved


def test_invalid_horizon_months():
    with pytest.raises(ValidationError):
        BranchOutcomeTargetRecord(**_valid_target(horizon_months=0))
    with pytest.raises(ValidationError):
        BranchOutcomeTargetRecord(**_valid_target(horizon_months=25))


def test_extra_fields_rejected():
    with pytest.raises(ValidationError, match="extra"):
        BranchOutcomeTargetRecord(**_valid_target(bogus="bad"))


def test_list_targets_for_branch(tmp_path: Path):
    save_target(BranchOutcomeTargetRecord(**_valid_target(branch_id="branch_A")), repo_root=tmp_path)
    save_target(BranchOutcomeTargetRecord(**_valid_target(branch_id="branch_B")), repo_root=tmp_path)
    all_targets = list_targets(repo_root=tmp_path)
    assert len(all_targets) == 2
    branch_a = [t for t in all_targets if t.branch_id == "branch_A"]
    assert len(branch_a) == 1


# --- Service tests ---

def test_evaluate_existing_target(tmp_path: Path):
    record = BranchOutcomeTargetRecord(**_valid_target(status="active"))
    save_target(record, repo_root=tmp_path)
    result = evaluate_existing_target(record.target_id, "fully deployed", True, repo_root=tmp_path)
    assert result.status == "achieved"
    assert result.final_observed_value == "fully deployed"


def test_cannot_evaluate_achieved_target(tmp_path: Path):
    record = BranchOutcomeTargetRecord(**_valid_target(status="achieved"))
    save_target(record, repo_root=tmp_path)
    with pytest.raises(ValueError, match="Cannot evaluate"):
        evaluate_existing_target(record.target_id, "again", True, repo_root=tmp_path)


# --- API tests ---

def test_api_health(client):
    resp = client.get("/branch-outcome-targets/health")
    assert resp.status_code == 200
    assert resp.json()["provider_required"] is False


def test_api_create_and_get(client):
    resp = client.post("/branch-outcome-targets", json=_valid_target())
    assert resp.status_code == 200
    target_id = resp.json()["target"]["target_id"]

    resp2 = client.get(f"/branch-outcome-targets/{target_id}")
    assert resp2.status_code == 200
    assert resp2.json()["target"]["target_id"] == target_id


def test_api_evaluate(client):
    resp = client.post("/branch-outcome-targets", json=_valid_target(status="active"))
    target_id = resp.json()["target"]["target_id"]

    resp2 = client.post(
        f"/branch-outcome-targets/{target_id}/evaluate",
        json={"final_observed_value": "shipped", "achieved": True},
    )
    assert resp2.status_code == 200
    assert resp2.json()["target"]["status"] == "achieved"


def test_api_list(client):
    client.post("/branch-outcome-targets", json=_valid_target())
    resp = client.get("/branch-outcome-targets/list")
    assert resp.status_code == 200
    assert resp.json()["count"] >= 1


def test_api_get_nonexistent(client):
    resp = client.get("/branch-outcome-targets/nonexistent_target_123")
    assert resp.status_code == 404
