"""
V1.0-rc Seeded Realistic Pilot — full product flow test.

Synthetic pilot scenario:
  Profile: Mid-career professional exploring career transition + health improvement
  Branch A (career_education): Upskill while employed, pursue data engineering role
  Branch B (health): Establish consistent exercise and sleep routine

  4 weeks of behavior metrics per branch
  1 outcome target per branch
  Branch forecasts → snapshots → external evidence → evaluations → scorecard
"""

import pytest
from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)

# Shared state across ordered tests (pytest runs in file order)
_state = {
    "profile_id": None,
    "career_target_id": None,
    "health_target_id": None,
    "forecast_a": None,
    "forecast_b": None,
    "snapshot_a_id": None,
    "snapshot_b_id": None,
    "evidence_career_id": None,
    "evidence_health_id": None,
    "evidence_wellbeing_id": None,
}


def _post(path, body, expect=200):
    r = client.post(path, json=body)
    assert r.status_code == expect, f"POST {path} failed: {r.status_code} {r.text}"
    return r.json()


def _get(path, expect=200):
    r = client.get(path)
    assert r.status_code == expect, f"GET {path} failed: {r.status_code} {r.text}"
    return r.json()


# ── Phase 1: Create predictor profile ────────────────────────────────────────

def test_01_create_predictor_profile():
    body = {
        "source_type": "structured_predictor_profile",
        "self_reported": True,
        "trait_baseline": {
            "conscientiousness": 0.65,
            "neuroticism_negative_emotionality": 0.45,
            "extraversion": 0.50,
            "agreeableness": 0.60,
            "openness": 0.70,
            "source": "short_self_report",
        },
        "current_context": {
            "education_status": "bachelor_degree_employed",
            "employment_status": "full_time_analyst",
            "financial_stability": "moderate_savings",
            "relationship_status": "partnered",
            "health_constraints": ["mild_back_pain"],
        },
        "prediction_targets": {
            "target_domains": ["career_education", "financial", "health", "subjective_wellbeing"],
            "time_horizon_months": 6,
        },
        "limitations": [
            "Self-reported traits, not validated instruments",
            "Single snapshot, no longitudinal baseline",
        ],
    }
    resp = _post("/predictor-profile", body)
    assert resp["status"] == "saved"
    profile = resp["profile"]
    assert profile["profile_id"].startswith("pp")
    assert profile["source_type"] == "structured_predictor_profile"
    assert profile["trait_baseline"]["conscientiousness"] == 0.65
    assert profile["current_context"]["education_status"] == "bachelor_degree_employed"
    _state["profile_id"] = profile["profile_id"]


# ── Phase 2: Create outcome targets ─────────────────────────────────────────

def test_02_create_career_outcome_target():
    body = {
        "branch_id": "branch_A",
        "domain": "career_education",
        "horizon_months": 6,
        "outcome_name": "Complete data engineering certification",
        "objective_definition": "Pass the AWS Data Engineer Associate certification exam with a score >= 700",
        "success_threshold": "Exam score >= 700 on first attempt",
        "measurement_method": "Official certification exam score report",
        "baseline_value": "No cloud certifications held",
        "target_value": "AWS Data Engineer Associate certified",
    }
    resp = _post("/branch-outcome-targets", body)
    assert resp["status"] == "saved"
    target = resp["target"]
    assert target["target_id"].startswith("bot")
    assert target["branch_id"] == "branch_A"
    assert target["domain"] == "career_education"
    assert target["status"] == "planned"
    _state["career_target_id"] = target["target_id"]


def test_03_create_health_outcome_target():
    body = {
        "branch_id": "branch_B",
        "domain": "health",
        "horizon_months": 6,
        "outcome_name": "Establish consistent exercise habit",
        "objective_definition": "Achieve 150+ minutes of moderate-vigorous activity per week for 4 consecutive weeks",
        "success_threshold": ">= 150 min/week for 4 consecutive weeks",
        "measurement_method": "Weekly behavior metric: moderate_vigorous_activity_minutes",
        "baseline_value": "~60 min/week sporadic",
        "target_value": ">= 150 min/week consistent",
    }
    resp = _post("/branch-outcome-targets", body)
    assert resp["status"] == "saved"
    target = resp["target"]
    assert target["target_id"].startswith("bot")
    assert target["branch_id"] == "branch_B"
    assert target["domain"] == "health"
    _state["health_target_id"] = target["target_id"]


# ── Phase 3: Create 4 weeks of behavior metrics ─────────────────────────────

def _week_body(week_id, start, end, branch_id, deep_work, follow_through,
               expense_days, sleep_nights, activity_min, social, abandoned):
    return {
        "record_id": week_id,
        "source_type": "weekly_behavior_metrics",
        "week_start": start,
        "week_end": end,
        "branch_id": branch_id,
        "career_education_deep_work_minutes": deep_work,
        "planned_commitment_follow_through_rate": follow_through,
        "expense_logged_days": expense_days,
        "regular_sleep_nights": sleep_nights,
        "moderate_vigorous_activity_minutes": activity_min,
        "meaningful_social_contact_count": social,
        "abandoned_committed_blocks": abandoned,
        "avoidable_health_risk_events": 0,
        "key_milestone_progress_pct": 0.0,
        "source_quality": "manual",
        "notes": f"Pilot week {week_id}",
    }


def test_04_create_week1_metrics():
    body = _week_body("pilot_w1", "2026-05-04", "2026-05-10", "branch_A",
                       deep_work=120, follow_through=0.7, expense_days=5,
                       sleep_nights=4, activity_min=45, social=3, abandoned=1)
    resp = _post("/behavior-metrics/weekly-records", body)
    assert resp["status"] == "saved"
    assert resp["record"]["record_id"] == "pilot_w1"


def test_05_create_week2_metrics():
    body = _week_body("pilot_w2", "2026-05-11", "2026-05-17", "branch_A",
                       deep_work=150, follow_through=0.75, expense_days=6,
                       sleep_nights=5, activity_min=60, social=2, abandoned=0)
    resp = _post("/behavior-metrics/weekly-records", body)
    assert resp["status"] == "saved"
    assert resp["record"]["record_id"] == "pilot_w2"


def test_06_create_week3_metrics():
    body = _week_body("pilot_w3", "2026-05-18", "2026-05-24", "branch_B",
                       deep_work=90, follow_through=0.8, expense_days=4,
                       sleep_nights=5, activity_min=90, social=4, abandoned=1)
    resp = _post("/behavior-metrics/weekly-records", body)
    assert resp["status"] == "saved"
    assert resp["record"]["record_id"] == "pilot_w3"


def test_07_create_week4_metrics():
    body = _week_body("pilot_w4", "2026-05-25", "2026-05-31", "branch_B",
                       deep_work=100, follow_through=0.85, expense_days=5,
                       sleep_nights=6, activity_min=120, social=3, abandoned=0)
    resp = _post("/behavior-metrics/weekly-records", body)
    assert resp["status"] == "saved"
    assert resp["record"]["record_id"] == "pilot_w4"


# ── Phase 4: Generate branch forecasts ───────────────────────────────────────

def test_08_forecast_branch_a_career():
    body = {
        "branch_id": "branch_A",
        "lookback_weeks": 4,
        "horizon_months": 6,
    }
    resp = _post("/branch-forecast/analyze", body)
    assert resp["branch_id"] == "branch_A"
    assert resp["horizon_months"] == 6
    assert "forecast_summary" in resp
    assert "route_a_personal_evidence" in resp
    assert "route_b_population_prior" in resp
    assert "personal_prior_adapter" in resp
    assert "domain_predictions" in resp

    # Verify no life_score or exact probability
    resp_str = str(resp)
    assert "life_score" not in resp_str.lower()
    assert "exact_probability" not in resp_str.lower()

    # Verify adapter integration
    adapter = resp["personal_prior_adapter"]
    assert "domain_results" in adapter
    assert "overall_alignment" in adapter
    assert "forecast_readiness" in adapter

    # Verify domain predictions have strength levels
    for dp in resp["domain_predictions"]:
        assert "strength_level" in dp
        assert dp["strength_level"] in ["strong_calibrated", "data_backed", "contextual", "none"]

    _state["forecast_a"] = resp


def test_09_forecast_branch_b_health():
    body = {
        "branch_id": "branch_B",
        "lookback_weeks": 4,
        "horizon_months": 6,
    }
    resp = _post("/branch-forecast/analyze", body)
    assert resp["branch_id"] == "branch_B"
    assert resp["horizon_months"] == 6
    assert "forecast_summary" in resp
    assert "personal_prior_adapter" in resp

    # Verify no life_score
    assert "life_score" not in str(resp).lower()

    _state["forecast_b"] = resp


# ── Phase 5: Lock forecast snapshots ────────────────────────────────────────

def test_10_snapshot_branch_a():
    forecast = _state["forecast_a"]
    assert forecast is not None, "forecast_a not set — run test_08 first"
    resp = _post("/forecast-snapshots/create-from-forecast", forecast)
    assert resp["status"] == "saved"
    snap = resp["snapshot"]
    assert snap["snapshot_id"].startswith("fs")
    assert snap["branch_id"] == "branch_A"
    assert snap["locked"] is True
    assert "forecast_payload" in snap
    assert "domain_predictions" in snap
    assert "adapter_summary" in snap
    assert "route_a_summary" in snap
    assert "route_b_summary" in snap

    # Verify adapter fields in domain predictions
    for dp in snap["domain_predictions"]:
        assert "adapter_adjusted_direction" in dp
        assert "adapter_conflict_level" in dp
        assert "adapter_alignment" in dp

    _state["snapshot_a_id"] = snap["snapshot_id"]


def test_11_snapshot_branch_b():
    forecast = _state["forecast_b"]
    assert forecast is not None, "forecast_b not set — run test_09 first"
    resp = _post("/forecast-snapshots/create-from-forecast", forecast)
    assert resp["status"] == "saved"
    snap = resp["snapshot"]
    assert snap["snapshot_id"].startswith("fs")
    assert snap["branch_id"] == "branch_B"
    assert snap["locked"] is True
    _state["snapshot_b_id"] = snap["snapshot_id"]


# ── Phase 6: Add external evidence ──────────────────────────────────────────

def test_12_evidence_career_positive():
    body = {
        "branch_id": "branch_A",
        "snapshot_id": _state["snapshot_a_id"],
        "domain": "career_education",
        "evidence_type": "exam_or_certification",
        "description": "Passed AWS Cloud Practitioner exam with score 820/1000. First step toward Data Engineer certification.",
        "objective_strength": "moderate",
        "polarity": "positive",
        "numeric_value": 820.0,
        "unit": "exam_score",
        "notes": "Pilot synthetic evidence — career path aligned with forecast direction",
    }
    resp = _post("/external-evidence", body)
    assert resp["status"] == "saved"
    ev = resp["evidence"]
    assert ev["evidence_id"].startswith("ee")
    assert ev["domain"] == "career_education"
    assert ev["polarity"] == "positive"
    _state["evidence_career_id"] = ev["evidence_id"]


def test_13_evidence_health_positive():
    body = {
        "branch_id": "branch_B",
        "snapshot_id": _state["snapshot_b_id"],
        "domain": "health",
        "evidence_type": "health_measurement",
        "description": "Completed 4 consecutive weeks of 120+ minutes moderate activity. Sleep averaging 6.5 hrs/night.",
        "objective_strength": "strong",
        "polarity": "positive",
        "numeric_value": 120.0,
        "unit": "minutes_per_week",
        "notes": "Pilot synthetic evidence — health improvement trajectory",
    }
    resp = _post("/external-evidence", body)
    assert resp["status"] == "saved"
    ev = resp["evidence"]
    assert ev["evidence_id"].startswith("ee")
    assert ev["domain"] == "health"
    _state["evidence_health_id"] = ev["evidence_id"]


def test_14_evidence_subjective_wellbeing():
    body = {
        "branch_id": "branch_A",
        "snapshot_id": _state["snapshot_a_id"],
        "domain": "subjective_wellbeing",
        "evidence_type": "user_or_customer_feedback",
        "description": "Self-reported energy levels improved. Weekly review notes show reduced anxiety about career direction.",
        "objective_strength": "weak",
        "polarity": "positive",
        "notes": "Pilot synthetic evidence — subjective wellbeing positive signal",
    }
    resp = _post("/external-evidence", body)
    assert resp["status"] == "saved"
    ev = resp["evidence"]
    assert ev["evidence_id"].startswith("ee")
    _state["evidence_wellbeing_id"] = ev["evidence_id"]


# ── Phase 7: Evaluate forecasts ─────────────────────────────────────────────

def test_15_evaluate_branch_a():
    body = {
        "snapshot_id": _state["snapshot_a_id"],
        "evidence_ids": [
            _state["evidence_career_id"],
            _state["evidence_wellbeing_id"],
        ],
        "force_final": False,
    }
    resp = _post("/forecast-evaluations/evaluate", body)
    assert resp["status"] == "saved"
    ev = resp["evaluation"]
    assert ev["evaluation_id"].startswith("fe")
    assert ev["snapshot_id"] == _state["snapshot_a_id"]
    assert ev["branch_id"] == "branch_A"
    assert ev["overall_result"] in ["hit", "miss", "partial", "unknown"]
    assert len(ev["domain_results"]) > 0

    # Verify per-source match results
    valid_match = ["hit", "miss", "partial", "unknown", None]
    for dr in ev["domain_results"]:
        assert "route_a_match_result" in dr
        assert "route_b_match_result" in dr
        assert "adapter_match_result" in dr
        assert dr["route_a_match_result"] in valid_match
        assert dr["route_b_match_result"] in valid_match
        assert dr["adapter_match_result"] in valid_match
        assert "conflict_level_at_forecast_time" in dr
        assert "evidence_alignment_at_forecast_time" in dr

    # Verify no life_score
    assert "life_score" not in str(resp).lower()


def test_16_evaluate_branch_b():
    body = {
        "snapshot_id": _state["snapshot_b_id"],
        "evidence_ids": [_state["evidence_health_id"]],
        "force_final": False,
    }
    resp = _post("/forecast-evaluations/evaluate", body)
    assert resp["status"] == "saved"
    ev = resp["evaluation"]
    assert ev["evaluation_id"].startswith("fe")
    assert ev["branch_id"] == "branch_B"
    assert ev["overall_result"] in ["hit", "miss", "partial", "unknown"]


# ── Phase 8: Generate scorecard ─────────────────────────────────────────────

def test_17_scorecard():
    resp = _get("/forecast-scorecard/summary")
    assert resp["status"] == "ok"
    sc = resp["scorecard"]
    assert sc["total_evaluations"] >= 2
    assert sc["hit_count"] + sc["miss_count"] + sc["partial_count"] + sc["unknown_count"] >= 2

    # Verify source hit rates exist
    shr = sc["source_hit_rates"]
    assert "route_a_hit_count" in shr
    assert "route_b_hit_count" in shr
    assert "adapter_hit_count" in shr
    assert "conflict_outcomes" in shr

    # Verify per-domain scores exist
    assert len(sc["by_domain"]) > 0

    # Verify calibration confidence
    assert sc["calibration_confidence"] in ["low", "medium", "high"]

    # Verify no life_score
    assert "life_score" not in str(sc).lower()


# ── Phase 9: Verify snapshots preserve adapter results ──────────────────────

def test_18_snapshot_preserves_adapter():
    resp = _get("/forecast-snapshots/list")
    assert resp["status"] == "ok"
    snapshots = resp["snapshots"]
    assert len(snapshots) >= 2

    for snap in snapshots:
        assert snap["locked"] is True
        assert "adapter_summary" in snap
        assert "route_a_summary" in snap
        assert "route_b_summary" in snap
        for dp in snap["domain_predictions"]:
            assert "adapter_adjusted_direction" in dp
            assert "adapter_conflict_level" in dp


# ── Phase 10: Verify list endpoints ─────────────────────────────────────────

def test_19_list_predictor_profiles():
    resp = _get("/predictor-profile/list")
    assert resp["status"] == "ok"
    assert resp["count"] >= 1
    assert len(resp["profiles"]) >= 1


def test_20_list_outcome_targets():
    resp = _get("/branch-outcome-targets/list")
    assert resp["status"] == "ok"
    assert resp["count"] >= 2
    assert len(resp["targets"]) >= 2


def test_21_list_behavior_metrics():
    resp = _get("/behavior-metrics/weekly-records")
    assert resp["status"] == "ok"
    assert resp["count"] >= 4
    assert len(resp["records"]) >= 4


def test_22_list_external_evidence():
    resp = _get("/external-evidence/list")
    assert resp["status"] == "ok"
    assert resp["count"] >= 3
    assert len(resp["evidence"]) >= 3


def test_23_list_evaluations():
    resp = _get("/forecast-evaluations/list")
    assert resp["status"] == "ok"
    assert resp["count"] >= 2
    assert len(resp["evaluations"]) >= 2


# ── Phase 11: Verify no forbidden constructs ────────────────────────────────

def test_24_no_life_score_anywhere():
    """Sweep all pilot endpoints for forbidden life_score field."""
    endpoints = [
        "/predictor-profile/list",
        "/branch-outcome-targets/list",
        "/behavior-metrics/weekly-records",
        "/forecast-snapshots/list",
        "/external-evidence/list",
        "/forecast-evaluations/list",
        "/forecast-scorecard/summary",
    ]
    for ep in endpoints:
        resp = _get(ep)
        assert "life_score" not in str(resp).lower(), f"life_score found in {ep}"


def test_25_no_exact_probability():
    """Verify no exact probability values are emitted in snapshots."""
    resp = _get("/forecast-snapshots/list")
    for snap in resp["snapshots"]:
        payload_str = str(snap.get("forecast_payload", {}))
        assert "exact_probability" not in payload_str.lower()
        assert "exact probability" not in payload_str.lower()
