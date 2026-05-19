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
    snapshot = _completed_snapshot()
    result = validate_snapshot_persist_governance(snapshot)
    assert result["valid"] is True

    bad_snapshot = snapshot.model_copy(
        update={"evidence_policy": EvidencePolicy(source_mode="self_report_only_phase0")}
    )
    result = validate_snapshot_persist_governance(bad_snapshot)
    assert result["valid"] is False
    assert any("source_mode" in e for e in result["errors"])

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
    audit = tmp_path / "audit.jsonl"
    result = persist_snapshot_to_disk(payload, target, "wrong-token", audit_path=audit)
    assert result["status"] == "rejected"
    assert "approval_token" in result["reason"]
    assert not target.exists()


def test_persist_writes_and_produces_audit_record(tmp_path):
    payload = build_snapshot_persist_payload(_completed_snapshot())
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"

    result = persist_snapshot_to_disk(payload, target, APPROVAL_TOKEN, audit_path=audit)
    assert result["status"] == "persisted"
    assert Path(result["path"]) == target
    assert result["sha256_before"] is None
    assert result["sha256_after"] is not None
    assert target.exists()
    assert target.read_text(encoding="utf-8") == payload["yaml_content"]
    assert audit.exists()
    lines = audit.read_text().strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["action"] == "snapshot_persist"


def test_persist_overwrites_existing_file(tmp_path):
    target = tmp_path / "snapshot.yaml"
    target.write_text("old content", encoding="utf-8")
    sha_before = sha256_text("old content")

    payload = build_snapshot_persist_payload(_completed_snapshot())
    audit = tmp_path / "audit.jsonl"

    result = persist_snapshot_to_disk(payload, target, APPROVAL_TOKEN, audit_path=audit)
    assert result["sha256_before"] == sha_before
    assert result["sha256_after"] != sha_before
    assert target.read_text(encoding="utf-8") == payload["yaml_content"]


# --- P3-001R contract repairs ---


def test_audit_record_stores_approval_token_hash_not_raw_token(tmp_path):
    payload = build_snapshot_persist_payload(_completed_snapshot())
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"

    result = persist_snapshot_to_disk(payload, target, APPROVAL_TOKEN, audit_path=audit)
    record = result["audit_record"]
    assert "approval_token_hash" in record
    assert "approval_token" not in record or record.get("approval_token") is None
    assert record["approval_token_hash"] == sha256_text(APPROVAL_TOKEN)


def test_audit_file_stores_approval_token_hash_not_raw(tmp_path):
    payload = build_snapshot_persist_payload(_completed_snapshot())
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"

    persist_snapshot_to_disk(payload, target, APPROVAL_TOKEN, audit_path=audit)
    lines = audit.read_text().strip().splitlines()
    record = json.loads(lines[0])
    assert "approval_token_hash" in record
    assert record["approval_token_hash"] == sha256_text(APPROVAL_TOKEN)


def test_dry_run_returns_200_without_writing_file(tmp_path):
    payload = build_snapshot_persist_payload(_completed_snapshot())
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"

    result = persist_snapshot_to_disk(
        payload, target, APPROVAL_TOKEN, dry_run=True, audit_path=audit
    )
    assert result["status"] == "dry_run"
    assert result["path"] is None
    assert not target.exists()
    assert not audit.exists()


def test_dry_run_response_includes_would_write(tmp_path):
    payload = build_snapshot_persist_payload(_completed_snapshot())
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"

    result = persist_snapshot_to_disk(
        payload, target, APPROVAL_TOKEN, dry_run=True, audit_path=audit
    )
    assert "would_write" in result
    assert result["would_write"] == payload["yaml_content"]


def test_dry_run_preserves_sha256_before(tmp_path):
    target = tmp_path / "snapshot.yaml"
    target.write_text("existing", encoding="utf-8")
    expected_sha = sha256_text("existing")

    payload = build_snapshot_persist_payload(_completed_snapshot())
    audit = tmp_path / "audit.jsonl"

    result = persist_snapshot_to_disk(
        payload, target, APPROVAL_TOKEN, dry_run=True, audit_path=audit
    )
    assert result["sha256_before"] == expected_sha


def test_active_yaml_hash_unchanged_after_persist(tmp_path):
    """When persisting to a temp path, the original active YAML must not change."""
    active_yaml = tmp_path / "alters" / "current" / "snapshot.yaml"
    active_yaml.parent.mkdir(parents=True)
    original_content = "original snapshot content"
    active_yaml.write_text(original_content, encoding="utf-8")
    original_hash = sha256_file(active_yaml)

    payload = build_snapshot_persist_payload(_completed_snapshot())
    audit = tmp_path / "audit.jsonl"

    # Persist to a different path — active YAML must remain untouched
    persist_target = tmp_path / "other" / "snapshot.yaml"
    persist_snapshot_to_disk(payload, persist_target, APPROVAL_TOKEN, audit_path=audit)

    assert sha256_file(active_yaml) == original_hash
    assert active_yaml.read_text(encoding="utf-8") == original_content


def test_score_yaml_not_created(tmp_path):
    payload = build_snapshot_persist_payload(_completed_snapshot())
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"

    persist_snapshot_to_disk(payload, target, APPROVAL_TOKEN, audit_path=audit)

    score_files = list(tmp_path.rglob("score_*.yaml"))
    assert score_files == []


def test_archive_folders_not_created(tmp_path):
    payload = build_snapshot_persist_payload(_completed_snapshot())
    target = tmp_path / "snapshot.yaml"
    audit = tmp_path / "audit.jsonl"

    persist_snapshot_to_disk(payload, target, APPROVAL_TOKEN, audit_path=audit)

    archive_dirs = list(tmp_path.rglob("archive"))
    assert archive_dirs == []


def test_persist_uses_dependency_injected_paths(tmp_path):
    payload = build_snapshot_persist_payload(_completed_snapshot())
    target = tmp_path / "custom" / "snapshot.yaml"
    audit = tmp_path / "custom" / "audit.jsonl"

    result = persist_snapshot_to_disk(payload, target, APPROVAL_TOKEN, audit_path=audit)
    assert result["status"] == "persisted"
    assert target.exists()
    assert audit.exists()


def test_persist_defaults_to_standard_paths(monkeypatch):
    """When no audit_path is provided, uses DEFAULT_AUDIT_PATH."""
    import alters_lab.services.snapshot_persist as mod

    called_paths = []
    original_mkdir = Path.mkdir

    def capturing_mkdir(self, *args, **kwargs):
        called_paths.append(str(self))
        return original_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", capturing_mkdir)

    payload = build_snapshot_persist_payload(_completed_snapshot())
    target = Path("/tmp/test_p3_001r_default/snapshot.yaml")

    # This will use DEFAULT_AUDIT_PATH — just verify the function accepts no audit_path
    result = persist_snapshot_to_disk(payload, target, "wrong-token")
    assert result["status"] == "rejected"
