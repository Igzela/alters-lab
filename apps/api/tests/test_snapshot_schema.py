import pytest

from alters_lab.schemas.snapshot import (
    AnchorName,
    IntakePhase,
    Snapshot,
    SnapshotAnchors,
    SnapshotIntakeStatus,
)


def test_empty_snapshot_is_valid():
    s = Snapshot()
    assert s.version == 1
    assert s.intake_status.phase == IntakePhase.not_started


def test_completed_snapshot_with_all_anchors_is_valid():
    s = Snapshot(
        anchors=SnapshotAnchors(
            heaviest_constraint="c1",
            most_unclear="c2",
            unwilling_to_give_up="c3",
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
    )
    assert s.intake_status.phase == IntakePhase.completed


def test_completed_snapshot_with_missing_anchor_is_rejected():
    with pytest.raises(ValueError, match="requires most_unclear"):
        Snapshot(
            anchors=SnapshotAnchors(
                heaviest_constraint="c1",
                most_unclear="",
                unwilling_to_give_up="c3",
            ),
            intake_status=SnapshotIntakeStatus(
                phase=IntakePhase.completed,
                completed_anchors=[
                    AnchorName.heaviest_constraint,
                    AnchorName.unwilling_to_give_up,
                ],
                pending_anchor=None,
            ),
        )


def test_version_below_1_rejected():
    with pytest.raises(ValueError, match="version must be >= 1"):
        Snapshot(version=0)
