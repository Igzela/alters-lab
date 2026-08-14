"""Materialize the deterministic public sample baseline for tests and local runs."""

from __future__ import annotations

import glob
import shutil
from pathlib import Path

import yaml


BASELINE_DATE = "2026-05-19"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _dump(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(data, handle, default_flow_style=False)


def materialize(project_root: Path = PROJECT_ROOT) -> None:
    sample = project_root / "alters" / "sample"
    current = project_root / "alters" / "current"
    current_alters = current / "alters"
    current_dialogue = current / "dialogue"
    current_alignment = current / "value_alignment"

    current_alters.mkdir(parents=True, exist_ok=True)
    current_dialogue.mkdir(parents=True, exist_ok=True)
    current_alignment.mkdir(parents=True, exist_ok=True)

    for name in ("snapshot.yaml", "branches.yaml", "reality_trace.yaml"):
        shutil.copy2(sample / name, current / name)
    for path in glob.glob(str(sample / "alters" / "alter_*.yaml")):
        shutil.copy2(path, current_alters / Path(path).name)

    for path in sorted(current_alters.glob("alter_*.yaml")):
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        data["generated_at"] = BASELINE_DATE
        data["time_horizon"] = "1.5-2年后"
        data["personality_drift"] = {"detected": False}
        _dump(path, data)

    reality_trace = current / "reality_trace.yaml"
    with reality_trace.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    current_probe = data.get("reality_trace", {}).get("current_probe", {})
    if "day_14_gate" in current_probe:
        current_probe["day_14_gate"]["status"] = "completed"
    _dump(reality_trace, data)

    _dump(
        current_alignment / f"alignment_{BASELINE_DATE}.yaml",
        {
            "value_alignment_report": {
                "status": "human_confirmed",
                "final_interpretation": {"primary_candidate": "branch_D"},
                "provisional_commitment": {
                    "selected_branch": "branch_D",
                    "selected_alter": "alter_D",
                },
            }
        },
    )
    _dump(
        current_dialogue / f"dialogue_alter_D_{BASELINE_DATE}.yaml",
        {
            "dialogue": {
                "status": "human_confirmed_static_artifact",
                "session": {"alter_ref": "alters/current/alters/alter_D.yaml"},
                "context_policy": {"provider_used": None, "runtime_used": False},
            }
        },
    )


if __name__ == "__main__":
    materialize()
