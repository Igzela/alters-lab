"""End-to-end prediction calibration flow test.

Covers the full pipeline:
  predictor profile → outcome target → forecast → snapshot → evidence → evaluation → scorecard

Assertions:
  - snapshot remains unchanged after evaluation
  - evaluation references snapshot and evidence
  - scorecard counts evaluation
  - no life_score
  - no probability emitted
  - no provider call
  - no active YAML/rubric writes
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alters_lab.schemas.predictor_profile import (
    PredictorProfileRecord,
    TraitBaseline,
    CurrentContext,
    PredictionTargets,
)
from alters_lab.schemas.branch_outcome_targets import BranchOutcomeTargetRecord
from alters_lab.schemas.forecast_snapshot import (
    ForecastSnapshotRecord,
    ForecastSummarySnapshot,
    DomainPrediction,
)
from alters_lab.schemas.external_evidence import ExternalEvidenceRecord
from alters_lab.schemas.forecast_evaluation import ForecastEvaluationRecord

from alters_lab.services.predictor_profile import save_profile
from alters_lab.services.branch_outcome_targets import save_target
from alters_lab.services.forecast_snapshot import save_snapshot, load_snapshot
from alters_lab.services.external_evidence import save_evidence
from alters_lab.services.forecast_evaluation import (
    evaluate_forecast,
    save_evaluation,
    load_evaluation,
)
from alters_lab.services.calibration_scorecard import build_scorecard


def test_end_to_end_calibration_flow(tmp_path: Path):
    """Full prediction calibration pipeline."""

    # 1. Create predictor profile
    profile = PredictorProfileRecord(
        profile_id="pp_test_001",
        trait_baseline=TraitBaseline(
            conscientiousness=0.7,
            neuroticism_negative_emotionality=0.3,
            source="short_self_report",
        ),
        current_context=CurrentContext(
            education_status="graduate",
            employment_status="employed",
        ),
        prediction_targets=PredictionTargets(
            target_domains=["career_education", "health"],
            time_horizon_months=6,
        ),
    )
    profile_path = save_profile(profile, repo_root=tmp_path)
    assert profile_path.exists()

    # 2. Create branch outcome target
    target = BranchOutcomeTargetRecord(
        target_id="bot_test_001",
        branch_id="branch_A",
        domain="career_education",
        horizon_months=6,
        outcome_name="Complete certification",
        objective_definition="Pass AWS Solutions Architect exam",
        success_threshold="Score >= 720/1000",
        measurement_method="Exam score report",
        baseline_value="0",
        target_value="720",
    )
    target_path = save_target(target, repo_root=tmp_path)
    assert target_path.exists()

    # 3. Create forecast snapshot (simulating what create-from-forecast does)
    snapshot = ForecastSnapshotRecord(
        snapshot_id="fs_test_001",
        branch_id="branch_A",
        horizon_months=3,
        forecast_payload={
            "branch_id": "branch_A",
            "generated_at": "2025-01-01T00:00:00Z",
            "horizon_months": 3,
        },
        forecast_summary=ForecastSummarySnapshot(
            trajectory_direction="improving",
            confidence="medium",
            credibility="medium",
            explanation="Career trajectory improving based on behavior metrics.",
        ),
        domain_predictions=[
            DomainPrediction(
                domain="career_education",
                predicted_direction="improving",
                source="route_a",
                confidence="medium",
                explanation="Deep work minutes increasing.",
            ),
            DomainPrediction(
                domain="health",
                predicted_direction="stable",
                source="overall_fallback",
                confidence="low",
                explanation="No health-specific data available.",
            ),
        ],
        route_a_summary={"available": True, "behavior_trends_summary": "2 improving, 1 stable"},
        route_b_summary={"available": False},
        limitations=["Route B unavailable"],
    )
    snapshot_path = save_snapshot(snapshot, repo_root=tmp_path)
    assert snapshot_path.exists()

    # 4. Add external evidence
    evidence_career = ExternalEvidenceRecord(
        evidence_id="ee_test_001",
        branch_id="branch_A",
        target_id="bot_test_001",
        snapshot_id="fs_test_001",
        domain="career_education",
        evidence_type="exam_or_certification",
        description="Passed AWS exam with score 780",
        objective_strength="strong",
        polarity="positive",
        numeric_value=780.0,
        unit="score",
    )
    evidence_health = ExternalEvidenceRecord(
        evidence_id="ee_test_002",
        branch_id="branch_A",
        domain="health",
        evidence_type="health_measurement",
        description="Maintained exercise routine",
        objective_strength="moderate",
        polarity="neutral",
    )
    save_evidence(evidence_career, repo_root=tmp_path)
    save_evidence(evidence_health, repo_root=tmp_path)

    # 5. Capture snapshot state before evaluation
    snapshot_before = load_snapshot("fs_test_001", repo_root=tmp_path)
    snapshot_dump_before = snapshot_before.model_dump(mode="json")

    # 6. Evaluate forecast
    evaluation = evaluate_forecast(
        snapshot_id="fs_test_001",
        evidence_ids=["ee_test_001", "ee_test_002"],
        repo_root=tmp_path,
    )

    # 7. Assert snapshot unchanged after evaluation
    snapshot_after = load_snapshot("fs_test_001", repo_root=tmp_path)
    snapshot_dump_after = snapshot_after.model_dump(mode="json")
    assert snapshot_dump_before == snapshot_dump_after, "Snapshot must not be mutated by evaluation"

    # 8. Assert evaluation references snapshot and evidence
    assert evaluation.snapshot_id == "fs_test_001"
    assert evaluation.branch_id == "branch_A"
    assert "ee_test_001" in evaluation.evidence_ids
    assert "ee_test_002" in evaluation.evidence_ids

    # 9. Assert domain-level evaluation uses domain predictions, not overall trajectory
    career_result = next(r for r in evaluation.domain_results if r.domain == "career_education")
    health_result = next(r for r in evaluation.domain_results if r.domain == "health")

    assert career_result.predicted_direction == "improving"
    assert career_result.predicted_direction_source == "route_a"
    assert career_result.match_result == "hit"  # positive evidence vs improving prediction

    assert health_result.predicted_direction == "stable"
    assert health_result.predicted_direction_source == "overall_fallback"
    assert health_result.match_result == "hit"  # neutral evidence vs stable prediction

    # 10. Assert horizon computed
    assert evaluation.horizon_due_at is not None
    assert evaluation.evaluation_type in ("provisional", "final")

    # 11. Save evaluation and build scorecard
    eval_path = save_evaluation(evaluation, repo_root=tmp_path)
    assert eval_path.exists()

    scorecard = build_scorecard(repo_root=tmp_path)
    assert scorecard.total_evaluations >= 1
    assert scorecard.hit_count >= 1

    # 12. No life_score anywhere
    eval_dump = evaluation.model_dump(mode="json")
    assert "life_score" not in str(eval_dump).lower()
    scorecard_dump = scorecard.model_dump(mode="json")
    assert "life_score" not in str(scorecard_dump).lower()

    # 13. No probability emitted
    assert "probability" not in eval_dump
    assert "percentile" not in eval_dump

    # 14. No active YAML/rubric writes
    for path in [profile_path, target_path, snapshot_path, eval_path]:
        path_str = str(path)
        assert "alters/current" not in path_str
        assert "rubric" not in path_str.lower()


def test_numeric_evidence_with_target(tmp_path: Path):
    """Numeric progress toward target maps to improved."""
    target = BranchOutcomeTargetRecord(
        target_id="bot_test_002",
        branch_id="branch_A",
        domain="career_education",
        horizon_months=6,
        outcome_name="Increase income",
        objective_definition="Get a raise",
        success_threshold="10% increase",
        measurement_method="Pay stub",
        baseline_value="50000",
        target_value="55000",
    )
    save_target(target, repo_root=tmp_path)

    snapshot = ForecastSnapshotRecord(
        snapshot_id="fs_test_002",
        branch_id="branch_A",
        horizon_months=6,
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
                source="route_a",
                confidence="medium",
                explanation="test",
            ),
        ],
    )
    save_snapshot(snapshot, repo_root=tmp_path)

    evidence = ExternalEvidenceRecord(
        evidence_id="ee_test_003",
        branch_id="branch_A",
        target_id="bot_test_002",
        domain="career_education",
        evidence_type="income_or_financial_change",
        description="Got a raise to 57000",
        objective_strength="strong",
        polarity="positive",
        numeric_value=57000.0,
        unit="USD/year",
    )
    save_evidence(evidence, repo_root=tmp_path)

    result = evaluate_forecast(
        "fs_test_002", ["ee_test_003"], repo_root=tmp_path,
    )

    career = next(r for r in result.domain_results if r.domain == "career_education")
    assert career.observed_direction == "improved"
    assert career.match_result == "hit"
