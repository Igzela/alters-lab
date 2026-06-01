"""Tests for calibration divergence service."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from alters_lab.schemas.calibration_divergence import CalibrationDivergenceRequest
from alters_lab.services.calibration_divergence import (
    _detect_divergence,
    _compute_subjective_direction,
    _aggregate_behavior_direction,
)


@pytest.fixture
def client():
    from alters_lab.main import app
    return TestClient(app)


# --- Unit tests for divergence logic ---

def test_diverging_positive_subjective():
    # Subjective improving + objective declining
    assert _detect_divergence("improving", "declining", "stable") == "diverging_positive_subjective"


def test_diverging_negative_subjective():
    # Subjective declining + objective improving
    assert _detect_divergence("declining", "improving", "stable") == "diverging_negative_subjective"


def test_both_improving_converging():
    assert _detect_divergence("improving", "improving", "stable") == "converging"


def test_both_declining_converging():
    assert _detect_divergence("declining", "declining", "stable") == "converging"


def test_insufficient_data():
    assert _detect_divergence("insufficient_data", "improving", "stable") == "insufficient_data"
    assert _detect_divergence("improving", "insufficient_data", "stable") == "insufficient_data"


def test_mixed_behavior():
    assert _detect_divergence("stable", "mixed", "stable") == "mixed"


def test_milestone_improving_with_declining_subjective():
    # Milestone improving counts as objective positive
    assert _detect_divergence("declining", "stable", "improving") == "diverging_negative_subjective"


def test_aggregate_behavior_direction_improving():
    assert _aggregate_behavior_direction(["improving", "improving", "stable"]) == "improving"


def test_aggregate_behavior_direction_declining():
    assert _aggregate_behavior_direction(["declining", "declining", "stable"]) == "declining"


def test_aggregate_behavior_direction_mixed():
    assert _aggregate_behavior_direction(["improving", "declining"]) == "mixed"


def test_aggregate_behavior_direction_empty():
    assert _aggregate_behavior_direction([]) == "insufficient_data"


# --- API tests ---

def test_api_analyze(client):
    resp = client.post(
        "/divergence-analysis/analyze",
        json={"lookback_weeks": 8},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "subjective_track" in data
    assert "objective_track" in data
    assert "divergence_status" in data
    assert "flags" in data
    assert "limitations" in data


def test_no_life_score_in_response(client):
    resp = client.post(
        "/divergence-analysis/analyze",
        json={"lookback_weeks": 8},
    )
    data = resp.json()
    assert "life_score" not in str(data).lower()


def test_divergence_status_is_valid_enum(client):
    resp = client.post(
        "/divergence-analysis/analyze",
        json={"lookback_weeks": 8},
    )
    data = resp.json()
    valid = {"converging", "diverging_positive_subjective", "diverging_negative_subjective", "mixed", "insufficient_data"}
    assert data["divergence_status"] in valid
