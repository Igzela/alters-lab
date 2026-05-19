from __future__ import annotations

from pathlib import Path

import yaml

from alters_lab.schemas.snapshot import IntakePhase, Snapshot


def snapshot_to_canonical_dict(snapshot: Snapshot) -> dict:
    """Return canonical YAML-ready dict with top-level 'snapshot:'.

    Requires snapshot.intake_status.phase == completed.
    Raises ValueError if snapshot is not completed.
    Must not mutate snapshot.
    """
    if snapshot.intake_status.phase != IntakePhase.completed:
        raise ValueError("snapshot must be completed before export")

    return {
        "snapshot": {
            "date": snapshot.date,
            "version": snapshot.version,
            "anchors": {
                "heaviest_constraint": snapshot.anchors.heaviest_constraint,
                "most_unclear": snapshot.anchors.most_unclear,
                "unwilling_to_give_up": snapshot.anchors.unwilling_to_give_up,
            },
            "context": {
                "current_commitments": snapshot.context.current_commitments,
                "external_deadlines": snapshot.context.external_deadlines,
                "energy_state": snapshot.context.energy_state,
            },
            "intake_status": {
                "phase": snapshot.intake_status.phase.value,
                "completed_anchors": [a.value for a in snapshot.intake_status.completed_anchors],
                "pending_anchor": None,
            },
            "evidence_policy": {
                "source_mode": snapshot.evidence_policy.source_mode,
                "confidence": snapshot.evidence_policy.confidence,
                "unresolved_assumptions": snapshot.evidence_policy.unresolved_assumptions,
            },
            "notes": snapshot.notes,
        }
    }


def snapshot_to_yaml(snapshot: Snapshot) -> str:
    """Return YAML string for a completed snapshot.

    Requires completed snapshot. Raises ValueError if not completed.
    Output includes top-level 'snapshot:'. Preserves Unicode and key order.
    """
    d = snapshot_to_canonical_dict(snapshot)
    return yaml.safe_dump(d, sort_keys=False, allow_unicode=True)


def write_snapshot_yaml(snapshot: Snapshot, target_path: Path, overwrite: bool = False) -> Path:
    """Write YAML only to explicit target_path.

    Requires completed snapshot. If target_path exists and overwrite is False,
    raise FileExistsError. Returns the path written.
    """
    if snapshot.intake_status.phase != IntakePhase.completed:
        raise ValueError("snapshot must be completed before export")

    target_path = Path(target_path)

    if target_path.exists() and not overwrite:
        raise FileExistsError(f"{target_path} already exists and overwrite=False")

    yaml_str = snapshot_to_yaml(snapshot)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(yaml_str, encoding="utf-8")
    return target_path
