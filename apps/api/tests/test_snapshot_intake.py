from alters_lab.schemas.snapshot import AnchorName, IntakePhase
from alters_lab.services.snapshot_intake import (
    create_empty_snapshot,
    mark_snapshot_completed,
    next_anchor,
    ready_for_confirmation,
    record_anchor_answer,
)


def test_create_empty_snapshot_pending_anchor_is_heaviest_constraint():
    s = create_empty_snapshot()
    assert s.intake_status.pending_anchor == AnchorName.heaviest_constraint
    assert s.intake_status.phase == IntakePhase.asking_heaviest_constraint


def test_next_anchor_returns_heaviest_constraint_first():
    s = create_empty_snapshot()
    assert next_anchor(s) == AnchorName.heaviest_constraint


def test_record_heaviest_constraint_advances_to_most_unclear():
    s = create_empty_snapshot()
    s2 = record_anchor_answer(s, AnchorName.heaviest_constraint, "I need to ship")
    assert s2.anchors.heaviest_constraint == "I need to ship"
    assert AnchorName.heaviest_constraint in s2.intake_status.completed_anchors
    assert s2.intake_status.pending_anchor == AnchorName.most_unclear


def test_record_most_unclear_advances_to_unwilling_to_give_up():
    s = create_empty_snapshot()
    s = record_anchor_answer(s, AnchorName.heaviest_constraint, "c1")
    s = record_anchor_answer(s, AnchorName.most_unclear, "c2")
    assert s.intake_status.pending_anchor == AnchorName.unwilling_to_give_up


def test_record_unwilling_to_give_up_advances_to_ready():
    s = create_empty_snapshot()
    s = record_anchor_answer(s, AnchorName.heaviest_constraint, "c1")
    s = record_anchor_answer(s, AnchorName.most_unclear, "c2")
    s = record_anchor_answer(s, AnchorName.unwilling_to_give_up, "c3")
    assert s.intake_status.phase == IntakePhase.ready_for_snapshot_confirmation
    assert s.intake_status.pending_anchor is None


def test_ready_for_confirmation_true_after_all_anchors():
    s = create_empty_snapshot()
    s = record_anchor_answer(s, AnchorName.heaviest_constraint, "c1")
    s = record_anchor_answer(s, AnchorName.most_unclear, "c2")
    s = record_anchor_answer(s, AnchorName.unwilling_to_give_up, "c3")
    assert ready_for_confirmation(s) is True


def test_mark_snapshot_completed_sets_phase():
    s = create_empty_snapshot()
    s = record_anchor_answer(s, AnchorName.heaviest_constraint, "c1")
    s = record_anchor_answer(s, AnchorName.most_unclear, "c2")
    s = record_anchor_answer(s, AnchorName.unwilling_to_give_up, "c3")
    s = mark_snapshot_completed(s)
    assert s.intake_status.phase == IntakePhase.completed
    assert s.intake_status.pending_anchor is None


def test_empty_answer_rejected():
    s = create_empty_snapshot()
    try:
        record_anchor_answer(s, AnchorName.heaviest_constraint, "")
        assert False, "should have raised ValueError"
    except ValueError:
        pass
    try:
        record_anchor_answer(s, AnchorName.heaviest_constraint, "   ")
        assert False, "should have raised ValueError"
    except ValueError:
        pass


def test_no_branch_orAlter_artifacts_from_service():
    """Service functions return Snapshot objects — no file writes, no branch/alter generation."""
    s = create_empty_snapshot()
    s = record_anchor_answer(s, AnchorName.heaviest_constraint, "c1")
    s = record_anchor_answer(s, AnchorName.most_unclear, "c2")
    s = record_anchor_answer(s, AnchorName.unwilling_to_give_up, "c3")
    s = mark_snapshot_completed(s)
    assert hasattr(s, "anchors")
    assert not hasattr(s, "branches")
    assert not hasattr(s, "alters")
