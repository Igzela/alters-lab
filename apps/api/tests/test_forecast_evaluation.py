"""Tests for forecast evaluation schema, service, and API."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi.testclient import TestClient
from pydantic import ValidationError

from alters_lab.schemas.forecast_evaluation import ForecastEvaluationRecord, DomainResult
from alters_lab.schemas.forecast_snapshot import (
    ForecastSnapshotRecord,
    ForecastSummarySnapshot,
    DomainPrediction,
)
from alters_lab.schemas.external_evidence import ExternalEvidenceRecord
from alters_lab.services.forecast_snapshot import save_snapshot, load_snapshot
from alters_lab.services.external_evidence import save_evidence
from alters_lab.services.forecast_evaluation import (
    evaluate_forecast,
    save_evaluation,
    load_evaluation,
    list_evaluations,
    _evaluate_direction,
    _aggregate_observed_direction,
    _infer_direction_from_numeric,
    _compute_horizon,
)


def _make_snapshot(
    tmp_path: Path,
    trajectory: str = "improving",
    snapshot_id: str | None = None,
    domain_predictions: list[DomainPrediction] | None = None,
    created_at: str | None = None,
    horizon_months: int = 3,
) -> ForecastSnapshotRecord:
    kwargs = dict(
        branch_id="branch_A",
        horizon_months=horizon_months,
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
    if domain_predictions is not None:
        kwargs["domain_predictions"] = domain_predictions
    if created_at:
        kwargs["created_at"] = created_at
    snapshot = ForecastSnapshotRecord(**kwargs)
    save_snapshot(snapshot, repo_root=tmp_path)
    return snapshot


def _make_evidence(
    tmp_path: Path,
    polarity: str = "positive",
    domain: str = "career_education",
    strength: str = "strong",
    numeric_value: float | None = None,
    target_id: str | None = None,
) -> ExternalEvidenceRecord:
    evidence = ExternalEvidenceRecord(
        branch_id="branch_A",
        domain=domain,
        evidence_type="milestone_completed",
        description=f"Test evidence: {polarity}",
        objective_strength=strength,
        polarity=polarity,
        numeric_value=numeric_value,
        target_id=target_id,
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
    assert _aggregate_observed_direction(e) == "improved"


def test_aggregate_polarity_negative():
    e = [ExternalEvidenceRecord(
        domain="career_education", evidence_type="other",
        description="test", objective_strength="weak", polarity="negative",
    )]
    assert _aggregate_observed_direction(e) == "declined"


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
    assert _aggregate_observed_direction(e) == "mixed"


def test_aggregate_polarity_empty():
    assert _aggregate_observed_direction([]) == "unknown"


# --- Numeric direction inference tests ---

def test_numeric_progress_toward_target():
    result = _infer_direction_from_numeric(85.0, "50.0", "100.0")
    assert result == "improved"


def test_numeric_movement_away_from_target():
    result = _infer_direction_from_numeric(30.0, "50.0", "100.0")
    assert result == "declined"


def test_numeric_lower_is_better():
    result = _infer_direction_from_numeric(5.0, "20.0", "0.0")
    assert result == "improved"


def test_numeric_missing_baseline():
    result = _infer_direction_from_numeric(85.0, None, "100.0")
    assert result is None


def test_numeric_missing_target():
    result = _infer_direction_from_numeric(85.0, "50.0", None)
    assert result is None


# --- Evaluation service tests ---

def test_domain_predictions_used_instead_of_trajectory(tmp_path: Path):
    """Career prediction can differ from health prediction."""
    domain_preds = [
        DomainPrediction(
            domain="career_education",
            predicted_direction="improving",
            source="route_a",
            confidence="medium",
            explanation="career improving",
        ),
        DomainPrediction(
            domain="health",
            predicted_direction="declining",
            source="route_a",
            confidence="low",
            explanation="health declining",
        ),
    ]
    snapshot = _make_snapshot(tmp_path, trajectory="stable", domain_predictions=domain_preds)
    e_career = _make_evidence(tmp_path, "positive", domain="career_education")
    e_health = _make_evidence(tmp_path, "negative", domain="health")

    result = evaluate_forecast(
        snapshot.snapshot_id, [e_career.evidence_id, e_health.evidence_id], repo_root=tmp_path,
    )

    career_result = next(r for r in result.domain_results if r.domain == "career_education")
    health_result = next(r for r in result.domain_results if r.domain == "health")

    assert career_result.predicted_direction == "improving"
    assert career_result.predicted_direction_source == "route_a"
    assert career_result.match_result == "hit"

    assert health_result.predicted_direction == "declining"
    assert health_result.predicted_direction_source == "route_a"
    assert health_result.match_result == "hit"


def test_unknown_domain_stays_unknown(tmp_path: Path):
    """Unknown domain direction stays unknown, not copied from overall."""
    snapshot = _make_snapshot(tmp_path, trajectory="improving", domain_predictions=[])
    # No domain predictions, no evidence -> predicted_direction should be unknown
    result = evaluate_forecast(snapshot.snapshot_id, [], repo_root=tmp_path)
    assert result.domain_results[0].predicted_direction == "unknown"
    assert result.domain_results[0].predicted_direction_source == "unknown"


def test_overall_fallback_marked(tmp_path: DomainPrediction):
    """Overall fallback is clearly marked."""
    domain_preds = [
        DomainPrediction(
            domain="career_education",
            predicted_direction="improving",
            source="overall_fallback",
            confidence="medium",
            explanation="Using overall trajectory direction as fallback.",
        ),
    ]
    snapshot = _make_snapshot(tmp_path, trajectory="improving", domain_predictions=domain_preds)
    evidence = _make_evidence(tmp_path, "positive", domain="career_education")
    result = evaluate_forecast(snapshot.snapshot_id, [evidence.evidence_id], repo_root=tmp_path)
    career = next(r for r in result.domain_results if r.domain == "career_education")
    assert career.predicted_direction_source == "overall_fallback"


def test_hit_when_predicted_and_observed_align(tmp_path: Path):
    domain_preds = [
        DomainPrediction(
            domain="career_education",
            predicted_direction="improving",
            source="route_a",
            confidence="medium",
            explanation="test",
        ),
    ]
    snapshot = _make_snapshot(tmp_path, "improving", domain_predictions=domain_preds)
    evidence = _make_evidence(tmp_path, "positive")
    result = evaluate_forecast(snapshot.snapshot_id, [evidence.evidence_id], repo_root=tmp_path)
    assert result.overall_result == "hit"
    assert result.domain_results[0].match_result == "hit"


def test_miss_when_predicted_and_observed_conflict(tmp_path: Path):
    domain_preds = [
        DomainPrediction(
            domain="career_education",
            predicted_direction="improving",
            source="route_a",
            confidence="medium",
            explanation="test",
        ),
    ]
    snapshot = _make_snapshot(tmp_path, "improving", domain_predictions=domain_preds)
    evidence = _make_evidence(tmp_path, "negative")
    result = evaluate_forecast(snapshot.snapshot_id, [evidence.evidence_id], repo_root=tmp_path)
    assert result.overall_result == "miss"
    assert result.domain_results[0].match_result == "miss"


def test_partial_when_mixed(tmp_path: Path):
    domain_preds = [
        DomainPrediction(
            domain="career_education",
            predicted_direction="improving",
            source="route_a",
            confidence="medium",
            explanation="test",
        ),
    ]
    snapshot = _make_snapshot(tmp_path, "improving", domain_predictions=domain_preds)
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


# --- Horizon elapsed tests ---

def test_evaluation_before_horizon_is_provisional(tmp_path: Path):
    now = datetime.now(timezone.utc)
    created_at = now.isoformat()
    snapshot = _make_snapshot(tmp_path, created_at=created_at, horizon_months=6)
    result = evaluate_forecast(snapshot.snapshot_id, [], repo_root=tmp_path)
    assert result.evaluation_type == "provisional"
    assert result.evaluation_horizon_elapsed is False
    assert result.days_until_due is not None
    assert result.days_until_due > 0


def test_evaluation_after_horizon_is_final(tmp_path: Path):
    old = datetime.now(timezone.utc) - timedelta(days=365)
    created_at = old.isoformat()
    snapshot = _make_snapshot(tmp_path, created_at=created_at, horizon_months=3)
    result = evaluate_forecast(snapshot.snapshot_id, [], repo_root=tmp_path)
    assert result.evaluation_type == "final"
    assert result.evaluation_horizon_elapsed is True
    assert result.days_until_due == 0


def test_force_final_before_horizon(tmp_path: Path):
    now = datetime.now(timezone.utc)
    created_at = now.isoformat()
    snapshot = _make_snapshot(tmp_path, created_at=created_at, horizon_months=12)
    result = evaluate_forecast(snapshot.snapshot_id, [], repo_root=tmp_path, force_final=True)
    assert result.evaluation_type == "final"
    assert result.evaluation_horizon_elapsed is True


def test_provisional_label_in_notes(tmp_path: Path):
    now = datetime.now(timezone.utc)
    snapshot = _make_snapshot(tmp_path, created_at=now.isoformat(), horizon_months=6)
    result = evaluate_forecast(snapshot.snapshot_id, [], repo_root=tmp_path)
    assert any("provisional" in note.lower() for note in result.calibration_notes)


def test_horizon_due_at_computed(tmp_path: Path):
    now = datetime.now(timezone.utc)
    snapshot = _make_snapshot(tmp_path, created_at=now.isoformat(), horizon_months=3)
    result = evaluate_forecast(snapshot.snapshot_id, [], repo_root=tmp_path)
    assert result.horizon_due_at is not None
    assert result.days_until_due is not None


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
        domain_predictions=[
            DomainPrediction(
                domain="career_education",
                predicted_direction="improving",
                source="overall_fallback",
                confidence="medium",
                explanation="test",
            ),
        ],
    )
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
    assert "probability" not in dumped
    assert "percentile" not in dumped


def test_scorecard_counts_unknown_separately(tmp_path: Path):
    """Unknown domain predictions are counted separately in scorecard."""
    snapshot = _make_snapshot(tmp_path, trajectory="improving", domain_predictions=[])
    result = evaluate_forecast(snapshot.snapshot_id, [], repo_root=tmp_path)
    assert result.overall_result == "unknown"
    save_evaluation(result, repo_root=tmp_path)
    from alters_lab.services.calibration_scorecard import build_scorecard
    scorecard = build_scorecard(repo_root=tmp_path)
    assert scorecard.unknown_count >= 1


# --- Domain-level field propagation tests ---

def test_domain_result_propagates_route_fields(tmp_path: Path):
    """DomainResult carries route_a_direction, route_b_prior_direction, transfer_risk from snapshot."""
    domain_preds = [
        DomainPrediction(
            domain="career_education",
            predicted_direction="improving",
            source="route_a",
            confidence="medium",
            explanation="test",
            route_a_direction="improving",
            route_b_prior_direction="favorable",
            evidence_strength="moderate",
            transfer_risk="low",
        ),
    ]
    snapshot = _make_snapshot(tmp_path, trajectory="stable", domain_predictions=domain_preds)
    evidence = _make_evidence(tmp_path, "positive", domain="career_education")
    result = evaluate_forecast(snapshot.snapshot_id, [evidence.evidence_id], repo_root=tmp_path)
    career = next(r for r in result.domain_results if r.domain == "career_education")
    assert career.route_a_direction == "improving"
    assert career.route_b_prior_direction == "favorable"
    assert career.transfer_risk == "low"


def test_overall_fallback_used_when_no_domain_predictions(tmp_path: Path):
    """When snapshot has no domain_predictions, evaluation uses unknown (not overall fallback)."""
    snapshot = _make_snapshot(tmp_path, trajectory="improving", domain_predictions=[])
    result = evaluate_forecast(snapshot.snapshot_id, [], repo_root=tmp_path)
    # With no domain predictions and no evidence, result is unknown
    assert result.overall_result == "unknown"
    assert all(r.predicted_direction == "unknown" for r in result.domain_results)
    assert all(r.predicted_direction_source == "unknown" for r in result.domain_results)


def test_domain_predictions_different_directions_evaluated_independently(tmp_path: Path):
    """Career improving + health declining evaluated against their own evidence."""
    domain_preds = [
        DomainPrediction(
            domain="career_education",
            predicted_direction="improving",
            source="route_a",
            confidence="medium",
            explanation="career up",
            route_a_direction="improving",
            route_b_prior_direction="favorable",
            transfer_risk="low",
        ),
        DomainPrediction(
            domain="health",
            predicted_direction="declining",
            source="route_b",
            confidence="low",
            explanation="health down",
            route_a_direction="unknown",
            route_b_prior_direction="unfavorable",
            transfer_risk="high",
        ),
    ]
    snapshot = _make_snapshot(tmp_path, trajectory="mixed", domain_predictions=domain_preds)
    e_career = _make_evidence(tmp_path, "positive", domain="career_education")
    e_health = _make_evidence(tmp_path, "negative", domain="health")

    result = evaluate_forecast(
        snapshot.snapshot_id,
        [e_career.evidence_id, e_health.evidence_id],
        repo_root=tmp_path,
    )

    career = next(r for r in result.domain_results if r.domain == "career_education")
    health = next(r for r in result.domain_results if r.domain == "health")

    assert career.match_result == "hit"
    assert health.match_result == "hit"
    assert career.predicted_direction_source == "route_a"
    assert health.predicted_direction_source == "route_b"
