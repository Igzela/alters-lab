import pytest
from pathlib import Path
from alters_lab.services.alter_rubric_baseline import (
    _direction_to_scores,
    build_baseline_from_alter,
    get_baseline_for_branch,
)


class TestDirectionToScores:
    def test_up(self):
        i, d30, d90 = _direction_to_scores("↑")
        assert i == 3 and d30 == 4 and d90 == 5

    def test_up_mixed(self):
        i, d30, d90 = _direction_to_scores("↑/mixed")
        assert i == 3 and d30 == 3 and d90 == 4

    def test_stable(self):
        i, d30, d90 = _direction_to_scores("→")
        assert i == 3 and d30 == 3 and d90 == 3

    def test_down_mixed(self):
        i, d30, d90 = _direction_to_scores("↓/mixed")
        assert i == 3 and d30 == 2 and d90 == 2

    def test_down(self):
        i, d30, d90 = _direction_to_scores("↓")
        assert i == 3 and d30 == 2 and d90 == 1

    def test_slash_down(self):
        i, d30, d90 = _direction_to_scores("→/↓")
        assert i == 3 and d30 == 2 and d90 == 2

    def test_unknown_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown drift direction"):
            _direction_to_scores("unknown")


class TestBuildBaseline:
    def test_alter_d(self):
        alter_data = {
            "id": "alter_D",
            "branch_ref": "branch_D",
            "personality_drift": {
                "execution_discipline": {"direction": "↑/mixed", "reason": "test"},
                "exploration_freedom": {"direction": "↑", "reason": "test"},
                "identity_stability": {"direction": "→", "reason": "test"},
                "risk_tolerance": {"direction": "↑", "reason": "test"},
                "engineering_closure": {"direction": "↑", "reason": "test"},
            },
        }
        baseline = build_baseline_from_alter(alter_data)
        assert baseline.alter_id == "alter_D"
        assert baseline.branch_id == "branch_D"
        # execution_discipline: ↑/mixed → (3,3,4)
        assert baseline.expected_initial.execution_discipline == 3
        assert baseline.expected_90d.execution_discipline == 4
        # exploration_freedom: ↑ → (3,4,5)
        assert baseline.expected_initial.exploration_freedom == 3
        assert baseline.expected_90d.exploration_freedom == 5
        # life_state_match: identity_stability(→→3) + risk_tolerance(↑→3) = round(avg(3,3))=3
        assert baseline.expected_initial.life_state_match == 3
        # energy_level: engineering_closure(↑→90d=5) + risk_tolerance(↑→90d=5) = avg(5,5)=5
        assert baseline.expected_90d.energy_level == 5

    def test_all_stable(self):
        alter_data = {
            "id": "alter_X",
            "branch_ref": "branch_X",
            "personality_drift": {
                "execution_discipline": {"direction": "→", "reason": "test"},
                "exploration_freedom": {"direction": "→", "reason": "test"},
                "identity_stability": {"direction": "→", "reason": "test"},
                "risk_tolerance": {"direction": "→", "reason": "test"},
                "engineering_closure": {"direction": "→", "reason": "test"},
            },
        }
        baseline = build_baseline_from_alter(alter_data)
        for dim in ("execution_discipline", "exploration_freedom", "life_state_match", "energy_level"):
            assert getattr(baseline.expected_initial, dim) == 3
            assert getattr(baseline.expected_30d, dim) == 3
            assert getattr(baseline.expected_90d, dim) == 3

    def test_contains_reasoning(self):
        alter_data = {
            "id": "alter_Y",
            "branch_ref": "branch_Y",
            "personality_drift": {
                "execution_discipline": {"direction": "↑", "reason": "r1"},
                "exploration_freedom": {"direction": "↓", "reason": "r2"},
                "identity_stability": {"direction": "→", "reason": "r3"},
                "risk_tolerance": {"direction": "↑/mixed", "reason": "r4"},
                "engineering_closure": {"direction": "↓/mixed", "reason": "r5"},
            },
        }
        baseline = build_baseline_from_alter(alter_data)
        assert "execution_discipline" in baseline.reasoning
        assert "exploration_freedom" in baseline.reasoning
        assert "life_state_match" in baseline.reasoning
        assert "energy_level" in baseline.reasoning

    def test_drift_direction_strings(self):
        alter_data = {
            "id": "alter_Z",
            "branch_ref": "branch_Z",
            "personality_drift": {
                "execution_discipline": {"direction": "↑", "reason": "r"},
                "exploration_freedom": {"direction": "↓", "reason": "r"},
                "identity_stability": {"direction": "→", "reason": "r"},
                "risk_tolerance": {"direction": "↑/mixed", "reason": "r"},
                "engineering_closure": {"direction": "→/↓", "reason": "r"},
            },
        }
        baseline = build_baseline_from_alter(alter_data)
        assert baseline.drift_direction["execution_discipline"] == "↑"
        assert baseline.drift_direction["exploration_freedom"] == "↓"
        assert baseline.drift_direction["life_state_match"] == "→+↑/mixed"
        assert baseline.drift_direction["energy_level"] == "→/↓+↑/mixed"


class TestGetBaselineForBranch:
    def test_returns_none_for_unknown_branch(self):
        result = get_baseline_for_branch("branch_ZZZ")
        assert result is None

    def test_loads_alter_d_baseline(self):
        """Real alter_D.yaml has identity_stability '↑/↓' — now mapped to neutral baseline."""
        result = get_baseline_for_branch("branch_D")
        assert result is not None
        assert result.branch_id == "branch_D"
        assert result.drift_direction["life_state_match"] == "↑/↓+↑"
