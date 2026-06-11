import pytest
from fastapi.testclient import TestClient
from alters_lab.main import app

client = TestClient(app)


class TestPredictionAccuracy:
    def test_no_branch_returns_empty(self):
        resp = client.get("/calibration-loop/prediction-accuracy?branch_id=branch_Z")
        assert resp.status_code == 200
        data = resp.json()
        assert data["branch_id"] == "branch_Z"
        assert data["baseline"] is None
        assert data["actual_trajectory"] == []
        assert data["accuracy"] is None
        assert len(data["limitations"]) > 0

    def test_branch_d_has_baseline(self):
        resp = client.get("/calibration-loop/prediction-accuracy?branch_id=branch_D")
        assert resp.status_code == 200
        data = resp.json()
        assert data["branch_id"] == "branch_D"
        # Should have baseline if alter_D.yaml exists
        if data["baseline"] is not None:
            assert "expected_initial" in data["baseline"]
            assert "expected_30d" in data["baseline"]
            assert "expected_90d" in data["baseline"]
            assert "drift_direction" in data["baseline"]

    def test_default_branch_is_d(self):
        resp = client.get("/calibration-loop/prediction-accuracy")
        assert resp.status_code == 200
        data = resp.json()
        assert data["branch_id"] == "branch_D"
