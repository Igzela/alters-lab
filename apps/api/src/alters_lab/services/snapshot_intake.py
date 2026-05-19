from __future__ import annotations

from alters_lab.schemas.snapshot import (
    AnchorName,
    IntakePhase,
    Snapshot,
    SnapshotAnchors,
    SnapshotContext,
    SnapshotIntakeStatus,
    EvidencePolicy,
)

ANCHOR_ORDER: list[AnchorName] = [
    AnchorName.heaviest_constraint,
    AnchorName.most_unclear,
    AnchorName.unwilling_to_give_up,
]


def create_empty_snapshot() -> Snapshot:
    return Snapshot(
        anchors=SnapshotAnchors(),
        context=SnapshotContext(),
        intake_status=SnapshotIntakeStatus(
            phase=IntakePhase.asking_heaviest_constraint,
            completed_anchors=[],
            pending_anchor=AnchorName.heaviest_constraint,
        ),
        evidence_policy=EvidencePolicy(),
    )


def next_anchor(snapshot: Snapshot) -> AnchorName | None:
    if snapshot.intake_status.phase == IntakePhase.completed:
        return None
    return snapshot.intake_status.pending_anchor


def record_anchor_answer(snapshot: Snapshot, anchor: AnchorName, answer: str) -> Snapshot:
    if not answer or not answer.strip():
        raise ValueError("answer must not be empty")

    anchors = snapshot.anchors.model_copy()
    intake = snapshot.intake_status.model_copy()

    setattr(anchors, anchor, answer.strip())

    if anchor not in intake.completed_anchors:
        intake.completed_anchors = [*intake.completed_anchors, anchor]

    answered = {a for a in intake.completed_anchors}
    next_pending = None
    for candidate in ANCHOR_ORDER:
        if candidate not in answered:
            next_pending = candidate
            break

    if next_pending is None:
        intake.phase = IntakePhase.ready_for_snapshot_confirmation
        intake.pending_anchor = None
    else:
        intake.pending_anchor = next_pending
        phase_map = {
            AnchorName.heaviest_constraint: IntakePhase.asking_heaviest_constraint,
            AnchorName.most_unclear: IntakePhase.asking_most_unclear,
            AnchorName.unwilling_to_give_up: IntakePhase.asking_unwilling_to_give_up,
        }
        intake.phase = phase_map[next_pending]

    return snapshot.model_copy(
        update={"anchors": anchors, "intake_status": intake}
    )


def ready_for_confirmation(snapshot: Snapshot) -> bool:
    return snapshot.intake_status.phase == IntakePhase.ready_for_snapshot_confirmation


def mark_snapshot_completed(snapshot: Snapshot) -> Snapshot:
    anchors = snapshot.anchors
    if not anchors.heaviest_constraint or not anchors.most_unclear or not anchors.unwilling_to_give_up:
        raise ValueError("all three anchors must be non-empty to complete")

    intake = snapshot.intake_status.model_copy()
    intake.phase = IntakePhase.completed
    intake.pending_anchor = None

    return snapshot.model_copy(update={"intake_status": intake})
