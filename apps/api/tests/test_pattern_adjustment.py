"""Tests for pattern adjustment service."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from alters_lab.schemas.pattern_adjustment import PatternAdjustmentRequest
from alters_lab.services.pattern_adjustment import adjust_forecast


def test_adjust_forecast_no_data(tmp_path: Path):
    request = PatternAdjustmentRequest(lookback_weeks=8, forecast_weeks=4)
    result = adjust_forecast(request, repo_root=tmp_path)
    assert result.has_patterns is False
    assert result.adjusted_forecast == []
    assert result.adjustments_applied == []


def test_adjust_forecast_no_patterns(tmp_path: Path):
    # Create scores but no pattern reviews
    scores_dir = tmp_path / "alters" / "product" / "calibration_records"
    scores_dir.mkdir(parents=True)

    for i in range(3):
        data = {
            "score_id": f"action_alignment_2026050{i+1}T120000Z_abcd{i:04d}",
            "session_id": f"session_{i}",
            "source_type": "weekly_review_session",
            "scores": {
                "direction_alignment": 0.6,
                "execution_consistency": 0.6,
                "avoidance_level": 0.3,
            },
            "action_alignment_score": 0.6333,
            "evidence": {
                "one_action_evidence": "test",
                "one_avoidance_or_friction_evidence": "test",
                "one_next_correction": "test",
            },
            "verdict_label": "aligned_progress",
            "verdict_sentence": "Test",
            "created_at": f"2026-05-0{i+1}T12:00:00+00:00",
        }
        (scores_dir / f"action_alignment_2026050{i+1}T120000Z_abcd{i:04d}.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
        )

    request = PatternAdjustmentRequest(lookback_weeks=8, forecast_weeks=4)
    result = adjust_forecast(request, repo_root=tmp_path)
    assert result.has_patterns is False
    assert len(result.adjusted_forecast) == 4
    # Without patterns, adjusted should equal original
    for adj in result.adjusted_forecast:
        assert adj.adjusted_score == adj.original_score


def test_adjust_forecast_with_pattern(tmp_path: Path):
    # Create scores
    scores_dir = tmp_path / "alters" / "product" / "calibration_records"
    scores_dir.mkdir(parents=True)

    for i in range(5):
        data = {
            "score_id": f"action_alignment_2026050{i+1}T120000Z_abcd{i:04d}",
            "session_id": f"session_{i}",
            "source_type": "weekly_review_session",
            "scores": {
                "direction_alignment": 0.5,
                "execution_consistency": 0.5,
                "avoidance_level": 0.4,
            },
            "action_alignment_score": 0.5667,
            "evidence": {
                "one_action_evidence": "test",
                "one_avoidance_or_friction_evidence": "test",
                "one_next_correction": "test",
            },
            "verdict_label": "noisy_progress",
            "verdict_sentence": "Test",
            "created_at": f"2026-05-0{i+1}T12:00:00+00:00",
        }
        (scores_dir / f"action_alignment_2026050{i+1}T120000Z_abcd{i:04d}.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
        )

    # Create a pattern review with triggered patterns
    patterns_dir = tmp_path / "alters" / "product" / "pattern_reviews"
    patterns_dir.mkdir(parents=True)

    pattern_data = {
        "review_id": "pattern_review_20260526T120000Z_abcd1234",
        "status": "pattern_triggered",
        "weeks_evaluated": 4,
        "triggered_patterns": [
            {
                "pattern": "repeated_noisy_progress",
                "occurrences": 3,
                "confidence": 0.85,
                "strategy_constraint": "Next week primary correction must directly reduce repeated_noisy_progress.",
            }
        ],
        "created_at": "2026-05-26T12:00:00+00:00",
    }
    (patterns_dir / "pattern_review_20260526T120000Z_abcd1234.yaml").write_text(
        yaml.safe_dump(pattern_data, sort_keys=False), encoding="utf-8"
    )

    request = PatternAdjustmentRequest(lookback_weeks=8, forecast_weeks=4)
    result = adjust_forecast(request, repo_root=tmp_path)
    assert result.has_patterns is True
    assert "repeated_noisy_progress" in result.adjustments_applied
    assert len(result.adjusted_forecast) == 4
    # Adjusted scores should be lower than original
    for adj in result.adjusted_forecast:
        assert adj.adjusted_score <= adj.original_score
        assert adj.adjustment_delta < 0
        assert adj.adjustment_reason != "No pattern adjustment"


def test_adjust_forecast_clamps_bounds(tmp_path: Path):
    # Create scores with very low values
    scores_dir = tmp_path / "alters" / "product" / "calibration_records"
    scores_dir.mkdir(parents=True)

    for i in range(5):
        data = {
            "score_id": f"action_alignment_2026050{i+1}T120000Z_abcd{i:04d}",
            "session_id": f"session_{i}",
            "source_type": "weekly_review_session",
            "scores": {
                "direction_alignment": 0.1,
                "execution_consistency": 0.1,
                "avoidance_level": 0.9,
            },
            "action_alignment_score": 0.1,
            "evidence": {
                "one_action_evidence": "test",
                "one_avoidance_or_friction_evidence": "test",
                "one_next_correction": "test",
            },
            "verdict_label": "avoidance_disguised_as_work",
            "verdict_sentence": "Test",
            "created_at": f"2026-05-0{i+1}T12:00:00+00:00",
        }
        (scores_dir / f"action_alignment_2026050{i+1}T120000Z_abcd{i:04d}.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
        )

    # Create pattern review with multiple triggered patterns
    patterns_dir = tmp_path / "alters" / "product" / "pattern_reviews"
    patterns_dir.mkdir(parents=True)

    pattern_data = {
        "review_id": "pattern_review_20260526T120000Z_abcd1234",
        "status": "pattern_triggered",
        "weeks_evaluated": 4,
        "triggered_patterns": [
            {
                "pattern": "repeated_avoidance_disguised_as_work",
                "occurrences": 4,
                "confidence": 0.9,
                "strategy_constraint": "Next week primary correction must directly reduce repeated_avoidance_disguised_as_work.",
            },
            {
                "pattern": "repeated_sleep_breakdown",
                "occurrences": 3,
                "confidence": 0.85,
                "strategy_constraint": "Next week primary correction must directly reduce repeated_sleep_breakdown.",
            },
        ],
        "created_at": "2026-05-26T12:00:00+00:00",
    }
    (patterns_dir / "pattern_review_20260526T120000Z_abcd1234.yaml").write_text(
        yaml.safe_dump(pattern_data, sort_keys=False), encoding="utf-8"
    )

    request = PatternAdjustmentRequest(lookback_weeks=8, forecast_weeks=4)
    result = adjust_forecast(request, repo_root=tmp_path)
    for adj in result.adjusted_forecast:
        assert 0.0 <= adj.adjusted_score <= 1.0
        assert 0.0 <= adj.lower_bound <= 1.0
        assert 0.0 <= adj.upper_bound <= 1.0
