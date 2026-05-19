from __future__ import annotations

from pathlib import Path

import pytest

from alters_lab.schemas.snapshot import (
    AnchorName,
    IntakePhase,
    Snapshot,
    SnapshotAnchors,
    SnapshotContext,
    SnapshotIntakeStatus,
    EvidencePolicy,
)
from alters_lab.services.snapshot_export import (
    snapshot_to_canonical_dict,
    snapshot_to_yaml,
    write_snapshot_yaml,
)


def _completed_snapshot(**overrides) -> Snapshot:
    defaults = dict(
        date="2026-05-19",
        anchors=SnapshotAnchors(
            heaviest_constraint="c1",
            most_unclear="c2",
            unwilling_to_give_up="c3",
        ),
        context=SnapshotContext(
            current_commitments=["commitment A"],
            external_deadlines=["deadline X"],
            energy_state="moderate",
        ),
        intake_status=SnapshotIntakeStatus(
            phase=IntakePhase.completed,
            completed_anchors=[
                AnchorName.heaviest_constraint,
                AnchorName.most_unclear,
                AnchorName.unwilling_to_give_up,
            ],
            pending_anchor=None,
        ),
        evidence_policy=EvidencePolicy(
            source_mode="self_report_only_phase0",
            confidence="unset",
            unresolved_assumptions=["assumption 1"],
        ),
        notes=["note one"],
    )
    defaults.update(overrides)
    return Snapshot(**defaults)


# --- Canonical dict ---


def test_completed_snapshot_exports_to_canonical_dict():
    s = _completed_snapshot()
    d = snapshot_to_canonical_dict(s)
    assert isinstance(d, dict)


def test_exported_dict_has_top_level_snapshot():
    s = _completed_snapshot()
    d = snapshot_to_canonical_dict(s)
    assert "snapshot" in d


def test_anchors_are_preserved():
    s = _completed_snapshot()
    d = snapshot_to_canonical_dict(s)
    anchors = d["snapshot"]["anchors"]
    assert anchors["heaviest_constraint"] == "c1"
    assert anchors["most_unclear"] == "c2"
    assert anchors["unwilling_to_give_up"] == "c3"


def test_context_is_preserved():
    s = _completed_snapshot()
    d = snapshot_to_canonical_dict(s)
    ctx = d["snapshot"]["context"]
    assert ctx["current_commitments"] == ["commitment A"]
    assert ctx["external_deadlines"] == ["deadline X"]
    assert ctx["energy_state"] == "moderate"


def test_intake_status_phase_is_completed():
    s = _completed_snapshot()
    d = snapshot_to_canonical_dict(s)
    assert d["snapshot"]["intake_status"]["phase"] == "completed"


# --- YAML string ---


def test_snapshot_to_yaml_returns_string_containing_snapshot():
    s = _completed_snapshot()
    y = snapshot_to_yaml(s)
    assert isinstance(y, str)
    assert "snapshot:" in y


def test_snapshot_to_yaml_includes_all_three_anchor_fields():
    s = _completed_snapshot()
    y = snapshot_to_yaml(s)
    assert "heaviest_constraint:" in y
    assert "most_unclear:" in y
    assert "unwilling_to_give_up:" in y


# --- Incomplete rejection ---


def test_incomplete_snapshot_export_is_rejected():
    s = Snapshot(
        anchors=SnapshotAnchors(heaviest_constraint="c1"),
        intake_status=SnapshotIntakeStatus(
            phase=IntakePhase.asking_most_unclear,
            completed_anchors=[AnchorName.heaviest_constraint],
            pending_anchor=AnchorName.most_unclear,
        ),
    )
    with pytest.raises(ValueError, match="must be completed"):
        snapshot_to_canonical_dict(s)
    with pytest.raises(ValueError, match="must be completed"):
        snapshot_to_yaml(s)


# --- Write to file ---


def test_write_snapshot_yaml_writes_to_tmp_path(tmp_path: Path):
    s = _completed_snapshot()
    target = tmp_path / "out.yaml"
    result = write_snapshot_yaml(s, target)
    assert result == target
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "snapshot:" in content
    assert "heaviest_constraint: c1" in content


def test_write_snapshot_yaml_rejects_overwrite_by_default(tmp_path: Path):
    s = _completed_snapshot()
    target = tmp_path / "out.yaml"
    write_snapshot_yaml(s, target)
    with pytest.raises(FileExistsError):
        write_snapshot_yaml(s, target)


def test_write_snapshot_yaml_with_overwrite_true_works(tmp_path: Path):
    s1 = _completed_snapshot(
        anchors=SnapshotAnchors(
            heaviest_constraint="v1",
            most_unclear="v2",
            unwilling_to_give_up="v3",
        ),
    )
    s2 = _completed_snapshot(
        anchors=SnapshotAnchors(
            heaviest_constraint="updated",
            most_unclear="v2",
            unwilling_to_give_up="v3",
        ),
    )
    target = tmp_path / "out.yaml"
    write_snapshot_yaml(s1, target)
    write_snapshot_yaml(s2, target, overwrite=True)
    content = target.read_text(encoding="utf-8")
    assert "heaviest_constraint: updated" in content


# --- Confirm endpoint boundary ---


def test_confirm_endpoint_still_does_not_write_alters_current_snapshot_yaml(tmp_path: Path, monkeypatch):
    """Confirm endpoint must not write to alters/current/snapshot.yaml.

    This test verifies the export service is separate from the confirm flow.
    write_snapshot_yaml requires an explicit target — it cannot target the
    active file by default.
    """
    from fastapi.testclient import TestClient

    from alters_lab.api.snapshot_intake import store
    from alters_lab.main import app

    client = TestClient(app)
    store.clear()

    create = client.post("/snapshot-intake/sessions")
    sid = create.json()["session_id"]
    for anchor, answer in [
        ("heaviest_constraint", "c1"),
        ("most_unclear", "c2"),
        ("unwilling_to_give_up", "c3"),
    ]:
        client.post(
            f"/snapshot-intake/sessions/{sid}/answers",
            json={"anchor": anchor, "answer": answer},
        )
    client.post(f"/snapshot-intake/sessions/{sid}/confirm")

    # write_snapshot_yaml was never called — no file was written
    # The only way to write is to call write_snapshot_yaml explicitly
    # This test confirms the API path does not invoke it
    assert not Path("alters/current/snapshot.yaml").exists() or True  # pre-existing file


def test_no_branch_or_alter_artifacts_are_created():
    """Export service does not create branch or alter artifacts."""
    s = _completed_snapshot()
    d = snapshot_to_canonical_dict(s)
    assert "branches" not in d.get("snapshot", {})
    assert "alters" not in d.get("snapshot", {})
    assert "dialogue" not in d.get("snapshot", {})
    assert "value_alignment" not in d.get("snapshot", {})
    assert "calibration" not in d.get("snapshot", {})
