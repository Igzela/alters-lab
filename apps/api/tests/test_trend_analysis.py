"""Tests for trend analysis service."""

from __future__ import annotations

from pathlib import Path

import pytest

from alters_lab.schemas.trend_analysis import TrendAnalysisRequest
from alters_lab.services.trend_analysis import (
    _classify_direction,
    _compute_confidence,
    _compute_consistency,
    _linear_regression,
    analyze_trend,
)


def test_linear_regression_two_points():
    slope, intercept, r_sq = _linear_regression([0.4, 0.6])
    assert slope == pytest.approx(0.2)
    assert r_sq == pytest.approx(1.0)


def test_linear_regression_flat_line():
    slope, intercept, r_sq = _linear_regression([0.5, 0.5, 0.5, 0.5])
    assert slope == pytest.approx(0.0)
    assert r_sq == pytest.approx(1.0)


def test_linear_regression_declining():
    slope, intercept, r_sq = _linear_regression([0.8, 0.6, 0.4, 0.2])
    assert slope < 0
    assert r_sq == pytest.approx(1.0)


def test_linear_regression_insufficient():
    slope, intercept, r_sq = _linear_regression([])
    assert slope == 0.0
    assert r_sq == 0.0

    slope, intercept, r_sq = _linear_regression([0.5])
    assert slope == 0.0


def test_classify_direction():
    assert _classify_direction(0.05) == "improving"
    assert _classify_direction(-0.05) == "declining"
    assert _classify_direction(0.0) == "stable"
    assert _classify_direction(0.01) == "stable"


def test_compute_confidence():
    assert _compute_confidence(8, 0.6) == "high"
    assert _compute_confidence(6, 0.5) == "high"
    assert _compute_confidence(5, 0.35) == "medium"
    assert _compute_confidence(4, 0.3) == "medium"
    assert _compute_confidence(3, 0.2) == "low"
    assert _compute_confidence(2, 0.9) == "low"


def test_compute_consistency():
    assert _compute_consistency([]) == 0.0
    assert _compute_consistency([0.5]) == 0.0
    assert _compute_consistency([0.5, 0.5, 0.5]) == 1.0
    assert _compute_consistency([0.2, 0.8]) < 0.5


def test_analyze_trend_insufficient_data(tmp_path: Path):
    request = TrendAnalysisRequest(lookback_weeks=4, forecast_weeks=4)
    result = analyze_trend(request, repo_root=tmp_path)
    assert result.overall_direction == "insufficient_data"
    assert result.forecast == []
    assert result.confidence_interval.data_count == 0


def test_analyze_trend_forecast_bounds(tmp_path: Path):
    # Create some action alignment score records
    scores_dir = tmp_path / "alters" / "product" / "calibration_records"
    scores_dir.mkdir(parents=True)

    for i in range(5):
        score = 0.4 + (i * 0.1)
        data = {
            "score_id": f"action_alignment_2026050{i+1}T120000Z_abcd{i:04d}",
            "session_id": f"session_{i}",
            "source_type": "weekly_review_session",
            "scores": {
                "direction_alignment": score,
                "execution_consistency": score,
                "avoidance_level": 1.0 - score,
            },
            "action_alignment_score": round(score, 4),
            "evidence": {
                "one_action_evidence": "test",
                "one_avoidance_or_friction_evidence": "test",
                "one_next_correction": "test",
            },
            "verdict_label": "aligned_progress",
            "verdict_sentence": "Test",
            "created_at": f"2026-05-0{i+1}T12:00:00+00:00",
        }
        import yaml
        (scores_dir / f"action_alignment_2026050{i+1}T120000Z_abcd{i:04d}.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
        )

    request = TrendAnalysisRequest(lookback_weeks=8, forecast_weeks=4)
    result = analyze_trend(request, repo_root=tmp_path)
    assert result.overall_direction == "improving"
    assert len(result.forecast) == 4
    for fp in result.forecast:
        assert 0.0 <= fp.predicted_score <= 1.0
        assert 0.0 <= fp.lower_bound <= 1.0
        assert 0.0 <= fp.upper_bound <= 1.0
        assert fp.lower_bound <= fp.predicted_score <= fp.upper_bound
