"""Map alter personality_drift directions to rubric dimension predictions.

Each alter YAML has a personality_drift section with 5 traits. This service
maps those traits to the 4 rubric dimensions used in calibration scoring:

  personality_drift trait  →  rubric dimension
  ─────────────────────────────────────────────
  execution_discipline     →  execution_discipline  (direct)
  exploration_freedom      →  exploration_freedom   (direct)
  identity_stability       →  life_state_match      (average with risk_tolerance)
  risk_tolerance           →  life_state_match      (average with identity_stability)
  engineering_closure      →  energy_level          (average with risk_tolerance)
  risk_tolerance           →  energy_level          (average with engineering_closure)

Direction → score mapping (initial / 30d / 90d):
  ↑        → 3 / 4 / 5
  ↑/mixed  → 3 / 3 / 4
  →        → 3 / 3 / 3
  →/↓ or ↓/mixed → 3 / 2 / 2
  ↓        → 3 / 2 / 1
"""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.calibration_loop import (
    AlterRubricBaseline,
    CalibrationScoreValues,
)
from alters_lab.services import io
from alters_lab.services.calibration_loop import get_repo_root
from alters_lab.services.p6_runtime import read_record, runtime_dir, write_record

_DIRECTION_SCORES: dict[str, tuple[int, int, int]] = {
    "↑": (3, 4, 5),
    "↑/mixed": (3, 3, 4),
    "↑/↓": (3, 3, 3),
    "→": (3, 3, 3),
    "→/↓": (3, 2, 2),
    "↓/mixed": (3, 2, 2),
    "↓": (3, 2, 1),
}


def _direction_to_scores(direction: str) -> tuple[int, int, int]:
    """Map a direction string to (initial, 30d, 90d) integer scores."""
    key = direction.strip()
    if key in _DIRECTION_SCORES:
        return _DIRECTION_SCORES[key]
    raise ValueError(f"Unknown drift direction: {direction!r}")


def _avg_score(direction_a: str, direction_b: str, index: int) -> int:
    """Average two direction scores at a given time index (0=initial, 1=30d, 2=90d)."""
    a = _direction_to_scores(direction_a)[index]
    b = _direction_to_scores(direction_b)[index]
    return round((a + b) / 2)


def build_baseline_from_alter(alter_data: dict) -> AlterRubricBaseline:
    """Build an AlterRubricBaseline from an already-loaded alter YAML dict.

    Maps personality_drift traits to the 4 rubric dimensions:
    - execution_discipline and exploration_freedom map directly.
    - life_state_match = average(identity_stability, risk_tolerance).
    - energy_level = average(engineering_closure, risk_tolerance).
    """
    drift: dict[str, dict[str, str]] = alter_data["personality_drift"]
    alter_id: str = alter_data["id"]
    branch_id: str = alter_data["branch_ref"]

    def direction(trait: str) -> str:
        return drift[trait]["direction"]

    # Per-dimension direction strings for drift_direction field
    drift_direction: dict[str, str] = {
        "execution_discipline": direction("execution_discipline"),
        "exploration_freedom": direction("exploration_freedom"),
        "life_state_match": f'{direction("identity_stability")}+{direction("risk_tolerance")}',
        "energy_level": f'{direction("engineering_closure")}+{direction("risk_tolerance")}',
    }

    def scores_for(trait: str) -> tuple[int, int, int]:
        return _direction_to_scores(direction(trait))

    ed = scores_for("execution_discipline")
    ef = scores_for("exploration_freedom")
    ls = tuple(
        _avg_score(direction("identity_stability"), direction("risk_tolerance"), i)
        for i in range(3)
    )
    el = tuple(
        _avg_score(direction("engineering_closure"), direction("risk_tolerance"), i)
        for i in range(3)
    )

    reasoning_parts = [
        f'execution_discipline: {direction("execution_discipline")}',
        f'exploration_freedom: {direction("exploration_freedom")}',
        f'life_state_match: avg(identity_stability {direction("identity_stability")}, risk_tolerance {direction("risk_tolerance")})',
        f'energy_level: avg(engineering_closure {direction("engineering_closure")}, risk_tolerance {direction("risk_tolerance")})',
    ]

    return AlterRubricBaseline(
        alter_id=alter_id,
        branch_id=branch_id,
        expected_initial=CalibrationScoreValues(
            execution_discipline=ed[0],
            exploration_freedom=ef[0],
            life_state_match=ls[0],
            energy_level=el[0],
        ),
        expected_30d=CalibrationScoreValues(
            execution_discipline=ed[1],
            exploration_freedom=ef[1],
            life_state_match=ls[1],
            energy_level=el[1],
        ),
        expected_90d=CalibrationScoreValues(
            execution_discipline=ed[2],
            exploration_freedom=ef[2],
            life_state_match=ls[2],
            energy_level=el[2],
        ),
        drift_direction=drift_direction,
        reasoning="; ".join(reasoning_parts),
    )


def get_baseline_for_branch(
    branch_id: str,
    repo_root: Path | None = None,
) -> AlterRubricBaseline | None:
    """Load the alter YAML for the given branch_id and build a baseline.

    branch_id "branch_A" maps to "alter_A", etc. Returns None if the
    alter YAML file does not exist.
    """
    alter_id = branch_id.replace("branch_", "alter_")
    root = repo_root or get_repo_root()
    alter_path = root / "alters" / "current" / "alters" / f"{alter_id}.yaml"
    alter_data = io.read_yaml(alter_path)
    if not isinstance(alter_data, dict):
        return None
    return build_baseline_from_alter(alter_data)


def save_baseline(
    baseline: AlterRubricBaseline,
    repo_root: Path | None = None,
) -> Path:
    """Persist a baseline to alters/product/alter_baselines/{alter_id}.yaml."""
    return write_record(
        area="alter_baselines",
        record_id=baseline.alter_id,
        data=baseline.model_dump(),
        repo_root=repo_root,
    )


def load_baseline(
    alter_id: str,
    repo_root: Path | None = None,
) -> AlterRubricBaseline | None:
    """Load a persisted baseline from alters/product/alter_baselines/{alter_id}.yaml."""
    try:
        data = read_record(
            area="alter_baselines",
            record_id=alter_id,
            repo_root=repo_root,
        )
    except FileNotFoundError:
        return None
    return AlterRubricBaseline(**data)
