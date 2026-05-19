from __future__ import annotations

import json
from pathlib import Path

import pytest

from alters_lab.schemas.branches import (
    Branch,
    BranchDiscoveryPayload,
    BranchDiscoveryStatus,
    BranchesPersistRequest,
)
from alters_lab.services.branches_persist import (
    branches_to_yaml,
    preview_branches_persist,
    validate_branches_governance,
    write_branches_with_audit,
)
from alters_lab.services.controlled_write import sha256_text


def _completed_branches_payload() -> BranchDiscoveryPayload:
    return BranchDiscoveryPayload(
        branch_discovery=BranchDiscoveryStatus(
            status="completed",
            source_snapshot_ref="alters/current/snapshot.yaml",
            confirmed_by="human_owner",
            confirmation_note="Test branches confirmed.",
        ),
        branches=[
            Branch(
                id="branch_A",
                label="Branch A",
                core_choice="choice A",
                structural_commitment="commitment A",
                key_tension_resolved="tension A",
                incompatible_with=["branch_B", "branch_C", "branch_D"],
            ),
            Branch(
                id="branch_B",
                label="Branch B",
                core_choice="choice B",
                structural_commitment="commitment B",
                key_tension_resolved="tension B",
                incompatible_with=["branch_A", "branch_C", "branch_D"],
            ),
            Branch(
                id="branch_C",
                label="Branch C",
                core_choice="choice C",
                structural_commitment="commitment C",
                key_tension_resolved="tension C",
                incompatible_with=["branch_A", "branch_B", "branch_D"],
            ),
            Branch(
                id="branch_D",
                label="Branch D",
                core_choice="choice D",
                structural_commitment="commitment D",
                key_tension_resolved="tension D",
                incompatible_with=["branch_A", "branch_B", "branch_C"],
            ),
        ],
    )


# --- branches_to_yaml ---


def test_branches_to_yaml_produces_valid_yaml():
    payload = _completed_branches_payload()
    y = branches_to_yaml(payload)
    assert "branch_discovery:" in y
    assert "branches:" in y
    assert "branch_A" in y


# --- validate_branches_governance ---


def test_governance_passes_for_valid_payload():
    payload = _completed_branches_payload()
    result = validate_branches_governance(payload)
    assert result["valid"] is True
    assert result["errors"] == []


def test_governance_rejects_incomplete_status():
    payload = _completed_branches_payload()
    payload.branch_discovery.status = "not_started"
    result = validate_branches_governance(payload)
    assert result["valid"] is False
    assert any("status" in e for e in result["errors"])


def test_governance_rejects_wrong_source_ref():
    payload = _completed_branches_payload()
    payload.branch_discovery.source_snapshot_ref = "wrong/path.yaml"
    result = validate_branches_governance(payload)
    assert result["valid"] is False
    assert any("source_snapshot_ref" in e for e in result["errors"])


def test_governance_rejects_wrong_branch_count():
    payload = _completed_branches_payload()
    payload.branches = payload.branches[:3]
    result = validate_branches_governance(payload)
    assert result["valid"] is False
    assert any("4 branches" in e for e in result["errors"])


def test_governance_rejects_wrong_branch_ids():
    payload = _completed_branches_payload()
    payload.branches[0].id = "branch_X"
    result = validate_branches_governance(payload)
    assert result["valid"] is False
    assert any("branch ids" in e for e in result["errors"])


def test_governance_rejects_empty_incompatible_with():
    payload = _completed_branches_payload()
    payload.branches[0].incompatible_with = []
    result = validate_branches_governance(payload)
    assert result["valid"] is False
    assert any("incompatible_with" in e for e in result["errors"])


# --- preview_branches_persist ---


def test_preview_does_not_write_target(tmp_path):
    payload = _completed_branches_payload()
    target = tmp_path / "branches.yaml"
    result = preview_branches_persist(payload, target)
    assert result["status"] == "dry_run"
    assert not target.exists()


def test_preview_preserves_pre_write_hash(tmp_path):
    payload = _completed_branches_payload()
    target = tmp_path / "branches.yaml"
    target.write_text("existing", encoding="utf-8")
    expected = sha256_text("existing")
    result = preview_branches_persist(payload, target)
    assert result["pre_write_hash"] == expected


# --- write_branches_with_audit ---


def test_write_accepts_arbitrary_token(tmp_path):
    payload = _completed_branches_payload()
    target = tmp_path / "branches.yaml"
    audit = tmp_path / "audit.jsonl"
    result = write_branches_with_audit(payload, target, audit, "any-token")
    assert result["status"] == "persisted"


def test_write_rejects_empty_token(tmp_path):
    payload = _completed_branches_payload()
    target = tmp_path / "branches.yaml"
    audit = tmp_path / "audit.jsonl"
    with pytest.raises(ValueError, match="approval_token"):
        write_branches_with_audit(payload, target, audit, "")


def test_write_rejects_whitespace_token(tmp_path):
    payload = _completed_branches_payload()
    target = tmp_path / "branches.yaml"
    audit = tmp_path / "audit.jsonl"
    with pytest.raises(ValueError, match="approval_token"):
        write_branches_with_audit(payload, target, audit, "   ")


def test_write_writes_canonical_yaml(tmp_path):
    payload = _completed_branches_payload()
    target = tmp_path / "branches.yaml"
    audit = tmp_path / "audit.jsonl"
    write_branches_with_audit(payload, target, audit, "test-token")
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "branch_discovery:" in content
    assert "branch_A" in content


def test_write_audit_includes_exact_token_hash(tmp_path):
    payload = _completed_branches_payload()
    target = tmp_path / "branches.yaml"
    audit = tmp_path / "audit.jsonl"
    raw_token = "human-approval-token-123"
    write_branches_with_audit(payload, target, audit, raw_token)
    lines = audit.read_text().strip().splitlines()
    record = json.loads(lines[0])
    assert record["approval_token_hash"] == sha256_text(raw_token)


def test_write_audit_does_not_contain_raw_token(tmp_path):
    payload = _completed_branches_payload()
    target = tmp_path / "branches.yaml"
    audit = tmp_path / "audit.jsonl"
    raw_token = "human-approval-token-123"
    write_branches_with_audit(payload, target, audit, raw_token)
    content = audit.read_text()
    assert raw_token not in content


def test_write_audit_operation_is_branches_persist(tmp_path):
    payload = _completed_branches_payload()
    target = tmp_path / "branches.yaml"
    audit = tmp_path / "audit.jsonl"
    write_branches_with_audit(payload, target, audit, "test-token")
    lines = audit.read_text().strip().splitlines()
    record = json.loads(lines[0])
    assert record["operation"] == "branches_persist"


def test_governance_failure_does_not_write(tmp_path):
    payload = BranchDiscoveryPayload(
        branch_discovery=BranchDiscoveryStatus(status="not_started"),
        branches=[],
    )
    target = tmp_path / "branches.yaml"
    audit = tmp_path / "audit.jsonl"
    result = write_branches_with_audit(payload, target, audit, "test-token")
    assert result["status"] == "rejected"
    assert not target.exists()


def test_governance_failure_does_not_append_audit(tmp_path):
    payload = BranchDiscoveryPayload(
        branch_discovery=BranchDiscoveryStatus(status="not_started"),
        branches=[],
    )
    target = tmp_path / "branches.yaml"
    audit = tmp_path / "audit.jsonl"
    write_branches_with_audit(payload, target, audit, "test-token")
    assert not audit.exists()


def test_backup_created_under_backup_dir(tmp_path):
    payload = _completed_branches_payload()
    target = tmp_path / "branches.yaml"
    target.write_text("old content", encoding="utf-8")
    audit = tmp_path / "audit.jsonl"
    backup_dir = tmp_path / "backups"
    write_branches_with_audit(
        payload, target, audit, "test-token",
        create_backup=True, backup_dir=backup_dir,
    )
    backups = list(backup_dir.glob("branches_*.yaml"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "old content"


def test_no_alter_dialogue_value_calibration_archive_files(tmp_path):
    payload = _completed_branches_payload()
    target = tmp_path / "branches.yaml"
    audit = tmp_path / "audit.jsonl"
    write_branches_with_audit(payload, target, audit, "test-token")
    for pattern in ["score_*.yaml", "archive", "alter_*.yaml", "dialogue_*.yaml", "alignment_*.yaml", "snapshot.yaml"]:
        matches = list(tmp_path.rglob(pattern))
        assert matches == [], f"Unexpected files matching {pattern}: {matches}"


# --- schema-level extra="forbid" defense ---


def test_branch_discovery_status_accepts_extra_fields():
    bs = BranchDiscoveryStatus(status="not_started", pipeline={"step_1": {"output": ["a"]}})
    d = bs.model_dump(mode="json")
    assert "pipeline" in d


def test_branch_rejects_extra_fields():
    with pytest.raises(Exception):
        Branch(
            id="branch_A", label="A", core_choice="c",
            structural_commitment="s", key_tension_resolved="t",
            incompatible_with=["branch_B"], calibration={"score": 0.9},
        )


def test_branch_discovery_payload_accepts_extra_fields():
    bp = BranchDiscoveryPayload(
        branch_discovery=BranchDiscoveryStatus(status="not_started"),
        pipeline={"step_1": {"output": ["a"]}},
    )
    d = bp.model_dump(mode="json")
    assert "pipeline" in d


def test_branches_persist_request_rejects_extra_fields():
    with pytest.raises(Exception):
        BranchesPersistRequest(
            approval_token="test",
            branch_discovery=BranchDiscoveryStatus(status="not_started"),
            provider={"name": "openai"},
        )
