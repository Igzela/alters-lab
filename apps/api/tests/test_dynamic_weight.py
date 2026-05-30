"""Tests for dynamic weight computation service."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from alters_lab.schemas.dynamic_weight import DynamicWeightRequest
from alters_lab.services.dynamic_weight import (
    _clamp_weight,
    compute_dynamic_weights,
)


def test_clamp_weight():
    assert _clamp_weight(0.1) == 0.5
    assert _clamp_weight(3.0) == 2.0
    assert _clamp_weight(1.0) == 1.0
    assert _clamp_weight(1.5) == 1.5


def test_dynamic_weights_no_data(tmp_path: Path):
    request = DynamicWeightRequest(lookback_weeks=8)
    result = compute_dynamic_weights(request, repo_root=tmp_path)
    assert result.status == "ok"
    assert len(result.weights) == 4
    assert all(w.weight == 1.0 for w in result.weights)
    assert result.overall_alignment == 0.0


def test_dynamic_weights_high_alignment(tmp_path: Path):
    scores_dir = tmp_path / "alters" / "product" / "calibration_records"
    scores_dir.mkdir(parents=True)

    for i in range(6):
        data = {
            "score_id": f"action_alignment_2026050{i+1}T120000Z_abcd{i:04d}",
            "session_id": f"session_{i}",
            "source_type": "weekly_review_session",
            "scores": {
                "direction_alignment": 0.8,
                "execution_consistency": 0.8,
                "avoidance_level": 0.1,
            },
            "action_alignment_score": 0.8333,
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

    request = DynamicWeightRequest(lookback_weeks=8)
    result = compute_dynamic_weights(request, repo_root=tmp_path)
    assert result.overall_alignment >= 0.7
    exec_weight = next(w for w in result.weights if w.dimension == "execution_discipline")
    assert exec_weight.weight <= 1.0  # reduced for high alignment
    explore_weight = next(w for w in result.weights if w.dimension == "exploration_freedom")
    assert explore_weight.weight >= 1.0  # boosted for high alignment


def test_dynamic_weights_low_alignment(tmp_path: Path):
    scores_dir = tmp_path / "alters" / "product" / "calibration_records"
    scores_dir.mkdir(parents=True)

    for i in range(6):
        data = {
            "score_id": f"action_alignment_2026050{i+1}T120000Z_abcd{i:04d}",
            "session_id": f"session_{i}",
            "source_type": "weekly_review_session",
            "scores": {
                "direction_alignment": 0.2,
                "execution_consistency": 0.2,
                "avoidance_level": 0.8,
            },
            "action_alignment_score": 0.2,
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

    request = DynamicWeightRequest(lookback_weeks=8)
    result = compute_dynamic_weights(request, repo_root=tmp_path)
    assert result.overall_alignment <= 0.3
    exec_weight = next(w for w in result.weights if w.dimension == "execution_discipline")
    assert exec_weight.weight >= 1.0  # boosted for low alignment
    energy_weight = next(w for w in result.weights if w.dimension == "energy_level")
    assert energy_weight.weight >= 1.0  # boosted due to high avoidance


def test_dynamic_weights_all_clamped(tmp_path: Path):
    request = DynamicWeightRequest(lookback_weeks=8)
    result = compute_dynamic_weights(request, repo_root=tmp_path)
    for w in result.weights:
        assert 0.5 <= w.weight <= 2.0
