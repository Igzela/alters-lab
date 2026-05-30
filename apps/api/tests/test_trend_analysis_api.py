"""Tests for trend analysis API endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_trend_analysis_health():
    response = client.get("/trend-analysis/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["component"] == "trend-analysis"
    assert data["provider_used"] is False
    assert data["active_write_allowed"] is False


def test_trend_analysis_analyze():
    response = client.post("/trend-analysis/analyze", json={
        "lookback_weeks": 8,
        "forecast_weeks": 4,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["overall_direction"] in ("improving", "declining", "stable", "insufficient_data")
    assert isinstance(data["forecast"], list)
    assert isinstance(data["confidence_interval"], dict)


def test_dynamic_weight_health():
    response = client.get("/dynamic-weight/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["component"] == "dynamic-weight"
    assert data["provider_used"] is False


def test_dynamic_weight_compute():
    response = client.post("/dynamic-weight/compute", json={
        "lookback_weeks": 8,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["weights"], list)
    assert len(data["weights"]) == 4
    assert isinstance(data["overall_alignment"], float)
    assert isinstance(data["recommendation"], str)


def test_pattern_adjustment_health():
    response = client.get("/pattern-adjustment/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["component"] == "pattern-adjustment"
    assert data["provider_used"] is False


def test_pattern_adjustment_adjust():
    response = client.post("/pattern-adjustment/adjust", json={
        "lookback_weeks": 8,
        "forecast_weeks": 4,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["has_patterns"], bool)
    assert isinstance(data["original_forecast"], list)
    assert isinstance(data["adjusted_forecast"], list)
    assert isinstance(data["adjustments_applied"], list)
