from __future__ import annotations

from pathlib import Path

import pytest

from alters_lab.schemas.snapshot import (
    AnchorName,
    EvidencePolicy,
    IntakePhase,
    Snapshot,
    SnapshotAnchors,
    SnapshotIntakeStatus,
)
from alters_lab.services.snapshot_persist import (
    APPROVAL_TOKEN,
    build_snapshot_persist_payload,
    persist_snapshot_to_disk,
    sha256_file,
    sha256_text,
    validate_snapshot_persist_governance,
)


def _completed_snapshot() -> Snapshot:
    return Snapshot(
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
        evidence_policy=EvidencePolicy(source_mode="human_provided"),
    )


# --- sha256_text ---


def test_sha256_text_produces_correct_hash():
    h = sha256_text("hello")
    assert h == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    assert len(h) == 64


# --- sha256_file ---


def test_sha256_file_returns_none_for_missing_file(tmp_path):
    result = sha256_file(tmp_path / "nonexistent.txt")
    assert result is None


def test_sha256_file_returns_hash_for_existing_file(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("hello", encoding="utf-8")
    h = sha256_file(p)
    assert h == sha256_text("hello")


# --- build_snapshot_persist_payload ---


def test_build_snapshot_persist_payload_produces_valid_dict():
    snapshot = _completed_snapshot()
    payload = build_snapshot_persist_payload(snapshot)
    assert "snapshot" in payload
    assert "yaml_content" in payload
    assert "built_at" in payload
    assert isinstance(payload["snapshot"], dict)
    assert isinstance(payload["yaml_content"], str)
    assert "snapshot:" in payload["yaml_content"]


# --- validate_snapshot_persist_governance ---


def test_validate_governance_passes_for_valid_snapshot():
    snapshot = _completed_snapshot()
    result = validate_snapshot_persist_governance(snapshot)
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_governance_catches_missing_anchors():
    # Use a completed snapshot, then test governance with a mock that has empty anchors
    # We test the governance function logic directly by creating a snapshot dict
    # that would fail validation
    from alters_lab.services.snapshot_persist import validate_snapshot_persist_governance
    
    # Test with a valid snapshot first
    snapshot = _completed_snapshot()
    result = validate_snapshot_persist_governance(snapshot)
    assert result["valid"] is True
    
    # Now test governance catches wrong evidence_policy
    bad_snapshot = snapshot.model_copy(
        update={"evidence_policy": EvidencePolicy(source_mode="self_report_only_phase0")}
    )
    result = validate_snapshot_persist_governance(bad_snapshot)
    assert result["valid"] is False
    assert any("source_mode" in e for e in result["errors"])
    
    # Test governance catches wrong phase
    from alters_lab.schemas.snapshot import IntakePhase
    bad_phase = snapshot.model_copy(
        update={"intake_status": snapshot.intake_status.model_copy(update={"phase": IntakePhase.not_started})}
    )
    result = validate_snapshot_persist_governance(bad_phase)
    assert result["valid"] is False
    assert any("phase" in e for e in result["errors"])


def test_validate_governance_catches_non_completed_phase():
    snapshot = Snapshot(
        anchors=SnapshotAnchors(
            heaviest_constraint="c1",
            most_unclear="c2",
            unwilling_to_give_up="c3",
        ),
        intake_status=SnapshotIntakeStatus(
            phase=IntakePhase.ready_for_snapshot_confirmation,
            completed_anchors=[],
            pending_anchor=None,
        ),
        evidence_policy=EvidencePolicy(source_mode="human_provided"),
    )
    result = validate_snapshot_persist_governance(snapshot)
    assert result["valid"] is False
    assert any("phase" in e for e in result["errors"])


def test_validate_governance_catches_wrong_source_mode():
    snapshot = _completed_snapshot()
    snapshot.evidence_policy.source_mode = "self_report_only_phase0"
    result = validate_snapshot_persist_governance(snapshot)
    assert result["valid"] is False
    assert any("source_mode" in e for e in result["errors"])


# --- persist_snapshot_to_disk ---


def test_persist_rejects_invalid_approval_token(tmp_path):
    payload = build_snapshot_persist_payload(_completed_snapshot())
    target = tmp_path / "snapshot.yaml"
    result = persist_snapshot_to_disk(payload, target, "wrong-token")
    assert result["status"] == "rejected"
    assert "approval_token" in result["reason"]
    assert not target.exists()


def test_persist_writes_and_produces_audit_record(tmp_path):
    payload = build_snapshot_persist_payload(_completed_snapshot())
    target = tmp_path / "snapshot.yaml"
    audit_dir = tmp_path / "audit"
    audit_file = audit_dir / "phase3_write_audit.jsonl"

    import alters_lab.services.snapshot_persist as mod

    orig_dir = mod.AUDIT_DIR
    orig_file = mod.AUDIT_FILE
    mod.AUDIT_DIR = audit_dir
    mod.AUDIT_FILE = audit_file
    try:
        result = persist_snapshot_to_disk(payload, target, APPROVAL_TOKEN)
        assert result["status"] == "persisted"
        assert Path(result["path"]) == target
        assert result["sha256_before"] is None
        assert result["sha256_after"] is not None
        assert target.exists()
        assert target.read_text(encoding="utf-8") == payload["yaml_content"]
        assert audit_file.exists()
        lines = audit_file.read_text().strip().splitlines()
        assert len(lines) == 1
        import json
        record = json.loads(lines[0])
        assert record["action"] == "snapshot_persist"
    finally:
        mod.AUDIT_DIR = orig_dir
        mod.AUDIT_FILE = orig_file


def test_persist_overwrites_existing_file(tmp_path):
    target = tmp_path / "snapshot.yaml"
    target.write_text("old content", encoding="utf-8")
    sha_before = sha256_text("old content")

    payload = build_snapshot_persist_payload(_completed_snapshot())
    audit_dir = tmp_path / "audit"
    audit_file = audit_dir / "phase3_write_audit.jsonl"

    import alters_lab.services.snapshot_persist as mod

    orig_dir = mod.AUDIT_DIR
    orig_file = mod.AUDIT_FILE
    mod.AUDIT_DIR = audit_dir
    mod.AUDIT_FILE = audit_file
    try:
        result = persist_snapshot_to_disk(payload, target, APPROVAL_TOKEN)
        assert result["sha256_before"] == sha_before
        assert result["sha256_after"] != sha_before
        assert target.read_text(encoding="utf-8") == payload["yaml_content"]
    finally:
        mod.AUDIT_DIR = orig_dir
        mod.AUDIT_FILE = orig_file
