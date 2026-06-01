"""Tests for calibration scorecard schema and service."""

from __future__ import annotations

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from alters_lab.schemas.calibration_scorecard import CalibrationScorecard
from alters_lab.schemas.forecast_evaluation import ForecastEvaluationRecord, DomainResult
from alters_lab.services.forecast_evaluation import save_evaluation
from alters_lab.services.calibration_scorecard import build_scorecard


def _make_evaluation(tmp_path: Path, overall: str = "hit", domain: str = "career_education", match: str = "hit") -> ForecastEvaluationRecord:
    ev = ForecastEvaluationRecord(
        snapshot_id="fs_test",
        branch_id="branch_A",
        domain_results=[DomainResult(
            domain=domain,
            predicted_direction="improving",
            observed_direction="improved" if match == "hit" else "declined",
            match_result=match,
            evidence_strength="strong",
        )],
        overall_result=overall,
        predictive_signals=["good signal"] if match == "hit" else [],
        misleading_signals=["bad signal"] if match == "miss" else [],
    )
    save_evaluation(ev, repo_root=tmp_path)
    return ev


# --- Schema tests ---

def test_scorecard_defaults():
    sc = CalibrationScorecard()
    assert sc.total_evaluations == 0
    assert sc.calibration_confidence == "low"


def test_scorecard_no_life_score():
    sc = CalibrationScorecard()
    dumped = sc.model_dump(mode="json")
    assert "life_score" not in str(dumped).lower()


# --- Service tests ---

def test_empty_evaluations(tmp_path: Path):
    sc = build_scorecard(repo_root=tmp_path)
    assert sc.total_evaluations == 0
    assert sc.calibration_confidence == "low"
    assert len(sc.limitations) > 0


def test_counts_hit_miss_partial_unknown(tmp_path: Path):
    _make_evaluation(tmp_path, "hit", match="hit")
    _make_evaluation(tmp_path, "miss", match="miss")
    _make_evaluation(tmp_path, "partial", match="partial")
    ev = ForecastEvaluationRecord(
        snapshot_id="fs_test", branch_id="branch_A",
        domain_results=[DomainResult(
            domain="career_education", predicted_direction="improving",
            observed_direction="unknown", match_result="unknown",
        )],
        overall_result="unknown",
    )
    save_evaluation(ev, repo_root=tmp_path)

    sc = build_scorecard(repo_root=tmp_path)
    assert sc.total_evaluations == 4
    assert sc.hit_count == 1
    assert sc.miss_count == 1
    assert sc.partial_count == 1
    assert sc.unknown_count == 1


def test_small_sample_returns_low_confidence(tmp_path: Path):
    for _ in range(3):
        _make_evaluation(tmp_path, "hit", match="hit")
    sc = build_scorecard(repo_root=tmp_path)
    assert sc.calibration_confidence == "low"
    assert any("low" in lim.lower() for lim in sc.limitations)


def test_medium_confidence_at_5(tmp_path: Path):
    for _ in range(5):
        _make_evaluation(tmp_path, "hit", match="hit")
    sc = build_scorecard(repo_root=tmp_path)
    assert sc.calibration_confidence == "medium"


def test_high_confidence_at_15(tmp_path: Path):
    for _ in range(15):
        _make_evaluation(tmp_path, "hit", match="hit")
    sc = build_scorecard(repo_root=tmp_path)
    assert sc.calibration_confidence == "high"


def test_by_domain_hit_rate(tmp_path: Path):
    _make_evaluation(tmp_path, "hit", domain="career_education", match="hit")
    _make_evaluation(tmp_path, "miss", domain="career_education", match="miss")
    sc = build_scorecard(repo_root=tmp_path)
    domain_scores = {d.domain: d for d in sc.by_domain}
    assert "career_education" in domain_scores
    assert domain_scores["career_education"].hit_rate == 0.5


def test_signal_quality(tmp_path: Path):
    _make_evaluation(tmp_path, "hit", match="hit")
    _make_evaluation(tmp_path, "miss", match="miss")
    sc = build_scorecard(repo_root=tmp_path)
    assert len(sc.signal_quality.predictive_signals) > 0
    assert len(sc.signal_quality.misleading_signals) > 0


# --- API tests ---

@pytest.fixture
def client():
    from alters_lab.main import app
    return TestClient(app)


def test_api_scorecard_summary(client):
    resp = client.get("/forecast-scorecard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "scorecard" in data
    assert "total_evaluations" in data["scorecard"]
    assert "calibration_confidence" in data["scorecard"]


def test_api_scorecard_no_life_score(client):
    resp = client.get("/forecast-scorecard/summary")
    assert "life_score" not in str(resp.json()).lower()
