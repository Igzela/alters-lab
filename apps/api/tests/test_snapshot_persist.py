from __future__ import annotations

import json
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
    build_snapshot_persist_payload,
    hash_approval_token,
    preview_snapshot_persist,
    sha256_file,
    sha256_text,
    validate_snapshot_persist_governance,
    write_snapshot_with_audit,
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


# --- hash_approval_token ---


def test_hash_approval_token_returns_exact_sha256():
    token = "human-approval-token-123"
    h = hash_approval_token(token)
    assert h == sha256_text(token)
    assert len(h) == 64


def test_hash_approval_token_rejects_empty():
    with pytest.raises(ValueError, match="approval_token"):
        hash_approval_token("")


def test_hash_approval_token_rejects_whitespace():
    with pytest.raises(ValueError, match="approval_token"):
        hash_approval_token("   ")


# --- no magic token import ---


def test_no_approval_token_constant():
    import alters_lab.services.snapshot_persist as mod

    assert not hasattr(mod, "APPROVAL_TOKEN")


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


def test_validate_governance_rejects_incomplete_phase():
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


def test_validate_governance_rejects_wrong_source_mode():
    snapshot = _completed_snapshot()
    snapshot.evidence_policy.source_mode = "self_report_only_phase0"
    result = validate_snapshot_persist_governance(snapshot)
    assert result["valid"] is False
    assert any("source_mode" in e for e in result["errors"])


# --- preview_snapshot_persist ---


def test_preview_does_not_write_target(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    result = preview_snapshot_persist(snapshot, target)
    assert result["status"] == "dry_run"
    assert not target.exists()


def test_preview_does_not_append_audit(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"
    preview_snapshot_persist(snapshot, target)
    assert not audit.exists()


def test_preview_preserves_pre_write_hash(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    target.write_text("existing", encoding="utf-8")
    expected = sha256_text("existing")
    result = preview_snapshot_persist(snapshot, target)
    assert result["pre_write_hash"] == expected


# --- write_snapshot_with_audit ---


def test_write_accepts_arbitrary_nonempty_token(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"
    result = write_snapshot_with_audit(snapshot, target, audit, "any-token-here")
    assert result["status"] == "persisted"


def test_write_rejects_empty_token(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"
    with pytest.raises(ValueError, match="approval_token"):
        write_snapshot_with_audit(snapshot, target, audit, "")


def test_write_rejects_whitespace_token(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"
    with pytest.raises(ValueError, match="approval_token"):
        write_snapshot_with_audit(snapshot, target, audit, "   ")


def test_write_writes_canonical_yaml(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"
    write_snapshot_with_audit(snapshot, target, audit, "test-token")
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "snapshot:" in content
    payload = build_snapshot_persist_payload(snapshot)
    assert content == payload["yaml_content"]


def test_write_audit_includes_exact_token_hash(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"
    raw_token = "human-approval-token-123"
    write_snapshot_with_audit(snapshot, target, audit, raw_token)
    lines = audit.read_text().strip().splitlines()
    record = json.loads(lines[0])
    assert record["approval_token_hash"] == sha256_text(raw_token)


def test_write_audit_does_not_contain_raw_token(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"
    raw_token = "human-approval-token-123"
    write_snapshot_with_audit(snapshot, target, audit, raw_token)
    content = audit.read_text()
    assert raw_token not in content


def test_write_audit_does_not_contain_approval_token_key(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"
    write_snapshot_with_audit(snapshot, target, audit, "test-token")
    lines = audit.read_text().strip().splitlines()
    record = json.loads(lines[0])
    assert "approval_token" not in record


def test_write_audit_does_not_contain_magic_token(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"
    write_snapshot_with_audit(snapshot, target, audit, "test-token")
    content = audit.read_text()
    assert "p3-001-approved" not in content


def test_backup_created_under_backup_dir(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    target.write_text("old content", encoding="utf-8")
    audit = tmp_path / "audit.jsonl"
    backup_dir = tmp_path / "backups"
    write_snapshot_with_audit(
        snapshot, target, audit, "test-token",
        create_backup=True, backup_dir=backup_dir,
    )
    backups = list(backup_dir.glob("snapshot_*.yaml"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "old content"


def test_backup_not_inside_alters_current(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    target.write_text("old content", encoding="utf-8")
    audit = tmp_path / "audit.jsonl"
    write_snapshot_with_audit(snapshot, target, audit, "test-token")
    alters_current = tmp_path / "alters" / "current"
    assert not alters_current.exists()


def test_governance_failure_does_not_write_target(tmp_path):
    snapshot = Snapshot(
        anchors=SnapshotAnchors(),
        intake_status=SnapshotIntakeStatus(phase=IntakePhase.not_started),
        evidence_policy=EvidencePolicy(source_mode="self_report_only_phase0"),
    )
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"
    result = write_snapshot_with_audit(snapshot, target, audit, "test-token")
    assert result["status"] == "rejected"
    assert not target.exists()


def test_governance_failure_does_not_append_pass_audit(tmp_path):
    snapshot = Snapshot(
        anchors=SnapshotAnchors(),
        intake_status=SnapshotIntakeStatus(phase=IntakePhase.not_started),
        evidence_policy=EvidencePolicy(source_mode="self_report_only_phase0"),
    )
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"
    write_snapshot_with_audit(snapshot, target, audit, "test-token")
    assert not audit.exists()


def test_no_branch_alter_dialogue_value_calibration_archive_files(tmp_path):
    snapshot = _completed_snapshot()
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"
    write_snapshot_with_audit(snapshot, target, audit, "test-token")
    for pattern in ["score_*.yaml", "archive", "alter_*.yaml", "dialogue_*.yaml", "alignment_*.yaml", "branches.yaml"]:
        matches = list(tmp_path.rglob(pattern))
        assert matches == [], f"Unexpected files matching {pattern}: {matches}"
