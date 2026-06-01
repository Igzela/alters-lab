"""Tests for forecast evaluation schema, service, and API."""

from __future__ import annotations

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from pydantic import ValidationError

from alters_lab.schemas.forecast_evaluation import ForecastEvaluationRecord, DomainResult
from alters_lab.schemas.forecast_snapshot import ForecastSnapshotRecord, ForecastSummarySnapshot
from alters_lab.schemas.external_evidence import ExternalEvidenceRecord
from alters_lab.services.forecast_snapshot import save_snapshot, load_snapshot
from alters_lab.services.external_evidence import save_evidence
from alters_lab.services.forecast_evaluation import (
    evaluate_forecast,
    save_evaluation,
    load_evaluation,
    list_evaluations,
    _evaluate_direction,
    _aggregate_polarity,
)


def _make_snapshot(tmp_path: Path, trajectory: str = "improving", snapshot_id: str | None = None) -> ForecastSnapshotRecord:
    kwargs = dict(
        branch_id="branch_A",
        horizon_months=3,
        forecast_payload={},
        forecast_summary=ForecastSummarySnapshot(
            trajectory_direction=trajectory,
            confidence="medium",
            credibility="medium",
            explanation="test",
        ),
        route_a_summary={"available": True},
        route_b_summary={"available": False},
        calibration_divergence_summary={"divergence_status": "insufficient_data"},
        limitations=["test limitation"],
    )
    if snapshot_id:
        kwargs["snapshot_id"] = snapshot_id
    snapshot = ForecastSnapshotRecord(**kwargs)
    save_snapshot(snapshot, repo_root=tmp_path)
    return snapshot


def _make_evidence(tmp_path: Path, polarity: str = "positive", domain: str = "career_education", strength: str = "strong") -> ExternalEvidenceRecord:
    evidence = ExternalEvidenceRecord(
        branch_id="branch_A",
        domain=domain,
        evidence_type="milestone_completed",
        description=f"Test evidence: {polarity}",
        objective_strength=strength,
        polarity=polarity,
    )
    save_evidence(evidence, repo_root=tmp_path)
    return evidence


# --- Direction evaluation tests ---

def test_direction_hit():
    assert _evaluate_direction("improving", "improved") == "hit"
    assert _evaluate_direction("declining", "declined") == "hit"
    assert _evaluate_direction("stable", "stable") == "hit"


def test_direction_miss():
    assert _evaluate_direction("improving", "declined") == "miss"
    assert _evaluate_direction("declining", "improved") == "miss"


def test_direction_partial():
    assert _evaluate_direction("improving", "stable") == "partial"
    assert _evaluate_direction("stable", "improved") == "partial"


def test_direction_unknown():
    assert _evaluate_direction("improving", "unknown") == "unknown"
    assert _evaluate_direction("unknown", "improved") == "unknown"


# --- Polarity aggregation tests ---

def test_aggregate_polarity_positive():
    e = [ExternalEvidenceRecord(
        domain="career_education", evidence_type="other",
        description="test", objective_strength="weak", polarity="positive",
    )]
    assert _aggregate_polarity(e) == "improved"


def test_aggregate_polarity_negative():
    e = [ExternalEvidenceRecord(
        domain="career_education", evidence_type="other",
        description="test", objective_strength="weak", polarity="negative",
    )]
    assert _aggregate_polarity(e) == "declined"


def test_aggregate_polarity_mixed():
    e = [
        ExternalEvidenceRecord(
            domain="career_education", evidence_type="other",
            description="test", objective_strength="weak", polarity="positive",
        ),
        ExternalEvidenceRecord(
            domain="career_education", evidence_type="other",
            description="test", objective_strength="weak", polarity="negative",
        ),
    ]
    assert _aggregate_polarity(e) == "mixed"


def test_aggregate_polarity_empty():
    assert _aggregate_polarity([]) == "unknown"


# --- Evaluation service tests ---

def test_hit_when_predicted_and_observed_align(tmp_path: Path):
    snapshot = _make_snapshot(tmp_path, "improving")
    evidence = _make_evidence(tmp_path, "positive")
    result = evaluate_forecast(snapshot.snapshot_id, [evidence.evidence_id], repo_root=tmp_path)
    assert result.overall_result == "hit"
    assert result.domain_results[0].match_result == "hit"


def test_miss_when_predicted_and_observed_conflict(tmp_path: Path):
    snapshot = _make_snapshot(tmp_path, "improving")
    evidence = _make_evidence(tmp_path, "negative")
    result = evaluate_forecast(snapshot.snapshot_id, [evidence.evidence_id], repo_root=tmp_path)
    assert result.overall_result == "miss"
    assert result.domain_results[0].match_result == "miss"


def test_partial_when_mixed(tmp_path: Path):
    snapshot = _make_snapshot(tmp_path, "improving")
    e1 = _make_evidence(tmp_path, "positive")
    e2 = _make_evidence(tmp_path, "negative")
    result = evaluate_forecast(snapshot.snapshot_id, [e1.evidence_id, e2.evidence_id], repo_root=tmp_path)
    assert result.domain_results[0].match_result == "partial"


def test_unknown_when_no_evidence(tmp_path: Path):
    snapshot = _make_snapshot(tmp_path)
    result = evaluate_forecast(snapshot.snapshot_id, [], repo_root=tmp_path)
    assert result.overall_result == "unknown"
    assert result.domain_results[0].match_result == "unknown"


def test_original_snapshot_unchanged(tmp_path: Path):
    snapshot = _make_snapshot(snapshot_id="fs_test_unchanged", tmp_path=tmp_path)
    evidence = _make_evidence(tmp_path, "negative")
    evaluate_forecast(snapshot.snapshot_id, [evidence.evidence_id], repo_root=tmp_path)
    loaded = load_snapshot(snapshot.snapshot_id, repo_root=tmp_path)
    assert loaded.forecast_summary.trajectory_direction == "improving"


def test_no_life_score(tmp_path: Path):
    snapshot = _make_snapshot(tmp_path)
    evidence = _make_evidence(tmp_path)
    result = evaluate_forecast(snapshot.snapshot_id, [evidence.evidence_id], repo_root=tmp_path)
    dumped = result.model_dump(mode="json")
    assert "life_score" not in str(dumped).lower()


def test_save_and_load_evaluation(tmp_path: Path):
    snapshot = _make_snapshot(tmp_path)
    evidence = _make_evidence(tmp_path)
    evaluation = evaluate_forecast(snapshot.snapshot_id, [evidence.evidence_id], repo_root=tmp_path)
    path = save_evaluation(evaluation, repo_root=tmp_path)
    assert path.exists()
    loaded = load_evaluation(evaluation.evaluation_id, repo_root=tmp_path)
    assert loaded.evaluation_id == evaluation.evaluation_id


def test_list_evaluations(tmp_path: Path):
    snapshot = _make_snapshot(tmp_path)
    evidence = _make_evidence(tmp_path)
    evaluation = evaluate_forecast(snapshot.snapshot_id, [evidence.evidence_id], repo_root=tmp_path)
    save_evaluation(evaluation, repo_root=tmp_path)
    evaluations = list_evaluations(repo_root=tmp_path)
    assert len(evaluations) == 1


# --- API tests ---

@pytest.fixture
def client():
    from alters_lab.main import app
    return TestClient(app)


def _create_snapshot_via_api(client) -> str:
    snapshot = ForecastSnapshotRecord(
        branch_id="branch_A",
        horizon_months=3,
        forecast_payload={},
        forecast_summary=ForecastSummarySnapshot(
            trajectory_direction="improving",
            confidence="medium",
            credibility="medium",
            explanation="test",
        ),
    )
    # Use service directly since API needs BranchForecastResult
    from alters_lab.services.forecast_snapshot import save_snapshot
    save_snapshot(snapshot)
    return snapshot.snapshot_id


def _create_evidence_via_api(client) -> str:
    resp = client.post("/external-evidence", json={
        "domain": "career_education",
        "evidence_type": "milestone_completed",
        "description": "Test evidence",
        "objective_strength": "strong",
        "polarity": "positive",
    })
    return resp.json()["evidence"]["evidence_id"]


def test_api_evaluate_hit(client):
    snapshot_id = _create_snapshot_via_api(client)
    evidence_id = _create_evidence_via_api(client)
    resp = client.post("/forecast-evaluations/evaluate", json={
        "snapshot_id": snapshot_id,
        "evidence_ids": [evidence_id],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "saved"
    assert data["evaluation"]["overall_result"] == "hit"


def test_api_evaluate_unknown_when_no_evidence(client):
    snapshot_id = _create_snapshot_via_api(client)
    resp = client.post("/forecast-evaluations/evaluate", json={
        "snapshot_id": snapshot_id,
        "evidence_ids": [],
    })
    assert resp.status_code == 200
    assert resp.json()["evaluation"]["overall_result"] == "unknown"


def test_api_evaluate_nonexistent_snapshot(client):
    resp = client.post("/forecast-evaluations/evaluate", json={
        "snapshot_id": "nonexistent",
        "evidence_ids": [],
    })
    assert resp.status_code == 404


def test_api_list_evaluations(client):
    snapshot_id = _create_snapshot_via_api(client)
    client.post("/forecast-evaluations/evaluate", json={
        "snapshot_id": snapshot_id,
        "evidence_ids": [],
    })
    resp = client.get("/forecast-evaluations/list")
    assert resp.status_code == 200
    assert resp.json()["count"] >= 1


def test_api_get_evaluation(client):
    snapshot_id = _create_snapshot_via_api(client)
    post_resp = client.post("/forecast-evaluations/evaluate", json={
        "snapshot_id": snapshot_id,
        "evidence_ids": [],
    })
    eval_id = post_resp.json()["evaluation"]["evaluation_id"]
    resp = client.get(f"/forecast-evaluations/{eval_id}")
    assert resp.status_code == 200
    assert resp.json()["evaluation"]["evaluation_id"] == eval_id


def test_api_get_nonexistent_evaluation(client):
    resp = client.get("/forecast-evaluations/nonexistent")
    assert resp.status_code == 404


def test_no_probability_emitted(tmp_path: Path):
    snapshot = _make_snapshot(tmp_path)
    evidence = _make_evidence(tmp_path)
    result = evaluate_forecast(snapshot.snapshot_id, [evidence.evidence_id], repo_root=tmp_path)
    dumped = result.model_dump(mode="json")
    # Should not contain probability-like fields
    assert "probability" not in dumped
    assert "percentile" not in dumped
