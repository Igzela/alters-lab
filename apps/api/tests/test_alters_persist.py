from __future__ import annotations

import json
from pathlib import Path

import pytest

from alters_lab.schemas.alters import AlterBatchPersistRequest, AlterPersistRequest, AlterPayload
from alters_lab.services.alters_persist import (
    alter_to_yaml,
    get_alter_target_path,
    preview_alter_persist,
    validate_alter_governance,
    validate_alter_raw_dict,
    validate_batch_governance,
    write_alter_batch_with_audit,
    write_alter_raw_batch_with_audit,
    write_alter_with_audit,
)
from alters_lab.services.controlled_write import sha256_text


def _valid_alter(alter_id: str = "alter_A") -> AlterPayload:
    branch_ref = alter_id.replace("alter_", "branch_")
    return AlterPayload(
        id=alter_id,
        branch_ref=branch_ref,
        label=f"Test {alter_id}",
        source_refs={
            "snapshot_ref": "alters/current/snapshot.yaml",
            "branches_ref": "alters/current/branches.yaml",
            "rubric_ref": "alters/calibration/rubric.yaml",
        },
        quality_status={"human_confirmed": True, "active": True},
        voice={"core_stance": "Test stance"},
    )


def _all_valid_alters() -> list[AlterPayload]:
    return [_valid_alter(aid) for aid in ("alter_A", "alter_B", "alter_C", "alter_D")]


# --- alter_to_yaml ---


def test_alter_to_yaml_produces_valid_yaml():
    alter = _valid_alter()
    y = alter_to_yaml(alter)
    assert "id: alter_A" in y
    assert "branch_ref: branch_A" in y


# --- validate_alter_governance ---


def test_governance_passes_for_valid_alter():
    alter = _valid_alter()
    result = validate_alter_governance(alter)
    assert result["valid"] is True


def test_governance_rejects_wrong_id():
    alter = _valid_alter()
    alter.id = "alter_X"
    result = validate_alter_governance(alter)
    assert result["valid"] is False


def test_governance_rejects_wrong_branch_ref():
    alter = _valid_alter()
    alter.branch_ref = "branch_X"
    result = validate_alter_governance(alter)
    assert result["valid"] is False


def test_governance_rejects_wrong_snapshot_ref():
    alter = _valid_alter()
    alter.source_refs.snapshot_ref = "wrong/path.yaml"
    result = validate_alter_governance(alter)
    assert result["valid"] is False


def test_governance_rejects_not_human_confirmed():
    alter = _valid_alter()
    alter.quality_status.human_confirmed = False
    result = validate_alter_governance(alter)
    assert result["valid"] is False


def test_governance_rejects_not_active():
    alter = _valid_alter()
    alter.quality_status.active = False
    result = validate_alter_governance(alter)
    assert result["valid"] is False


def test_governance_rejects_empty_voice():
    alter = _valid_alter()
    alter.voice.core_stance = ""
    result = validate_alter_governance(alter)
    assert result["valid"] is False


# --- validate_batch_governance ---


def test_batch_governance_passes_for_all_valid():
    result = validate_batch_governance(_all_valid_alters())
    assert result["valid"] is True


def test_batch_governance_rejects_if_any_invalid():
    alters = _all_valid_alters()
    alters[0].id = "alter_X"
    result = validate_batch_governance(alters)
    assert result["valid"] is False


# --- preview_alter_persist ---


def test_preview_does_not_write(tmp_path):
    alter = _valid_alter()
    target = tmp_path / "alter_A.yaml"
    result = preview_alter_persist(alter, target)
    assert result["status"] == "dry_run"
    assert not target.exists()


# --- write_alter_with_audit ---


def test_write_accepts_arbitrary_token(tmp_path):
    alter = _valid_alter()
    target = tmp_path / "alter_A.yaml"
    audit = tmp_path / "audit.jsonl"
    result = write_alter_with_audit(alter, target, audit, "any-token")
    assert result["status"] == "persisted"


def test_write_rejects_empty_token(tmp_path):
    alter = _valid_alter()
    target = tmp_path / "alter_A.yaml"
    audit = tmp_path / "audit.jsonl"
    with pytest.raises(ValueError, match="approval_token"):
        write_alter_with_audit(alter, target, audit, "")


def test_write_writes_canonical_yaml(tmp_path):
    alter = _valid_alter()
    target = tmp_path / "alter_A.yaml"
    audit = tmp_path / "audit.jsonl"
    write_alter_with_audit(alter, target, audit, "test-token")
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "id: alter_A" in content


def test_write_audit_includes_exact_hash(tmp_path):
    alter = _valid_alter()
    target = tmp_path / "alter_A.yaml"
    audit = tmp_path / "audit.jsonl"
    raw_token = "human-approval-token-123"
    write_alter_with_audit(alter, target, audit, raw_token)
    lines = audit.read_text().strip().splitlines()
    record = json.loads(lines[0])
    assert record["approval_token_hash"] == sha256_text(raw_token)


def test_write_audit_no_raw_token(tmp_path):
    alter = _valid_alter()
    target = tmp_path / "alter_A.yaml"
    audit = tmp_path / "audit.jsonl"
    raw_token = "human-approval-token-123"
    write_alter_with_audit(alter, target, audit, raw_token)
    content = audit.read_text()
    assert raw_token not in content


def test_write_audit_operation_is_alter_persist(tmp_path):
    alter = _valid_alter()
    target = tmp_path / "alter_A.yaml"
    audit = tmp_path / "audit.jsonl"
    write_alter_with_audit(alter, target, audit, "test-token")
    lines = audit.read_text().strip().splitlines()
    record = json.loads(lines[0])
    assert record["operation"] == "alter_persist"


def test_governance_failure_does_not_write(tmp_path):
    alter = _valid_alter()
    alter.id = "alter_X"
    target = tmp_path / "alter_X.yaml"
    audit = tmp_path / "audit.jsonl"
    result = write_alter_with_audit(alter, target, audit, "test-token")
    assert result["status"] == "rejected"
    assert not target.exists()


# --- write_alter_batch_with_audit ---


def test_batch_write_all_valid(tmp_path):
    alters = _all_valid_alters()
    base_dir = tmp_path / "alters"
    audit = tmp_path / "audit.jsonl"
    result = write_alter_batch_with_audit(alters, base_dir, audit, "test-token")
    assert result["status"] == "persisted"
    assert len(result["written_paths"]) == 4
    for aid in ("alter_A", "alter_B", "alter_C", "alter_D"):
        assert (base_dir / f"{aid}.yaml").exists()


def test_batch_write_rejects_if_any_invalid(tmp_path):
    alters = _all_valid_alters()
    alters[0].id = "alter_X"
    base_dir = tmp_path / "alters"
    audit = tmp_path / "audit.jsonl"
    result = write_alter_batch_with_audit(alters, base_dir, audit, "test-token")
    assert result["status"] == "rejected"
    assert not (base_dir / "alter_A.yaml").exists()
    assert not audit.exists()


def test_batch_audit_operation_is_alters_batch_persist(tmp_path):
    alters = _all_valid_alters()
    base_dir = tmp_path / "alters"
    audit = tmp_path / "audit.jsonl"
    write_alter_batch_with_audit(alters, base_dir, audit, "test-token")
    lines = audit.read_text().strip().splitlines()
    record = json.loads(lines[0])
    assert record["operation"] == "alters_batch_persist"


def test_get_alter_target_path(tmp_path):
    p = get_alter_target_path("alter_A", tmp_path)
    assert p == tmp_path / "alter_A.yaml"


# --- schema-level extra="forbid" defense ---


def test_alter_source_refs_rejects_extra_fields():
    with pytest.raises(Exception):
        AlterSourceRefs(
            snapshot_ref="alters/current/snapshot.yaml",
            dialogue=True,
        )


def test_alter_payload_rejects_extra_fields():
    with pytest.raises(Exception):
        AlterPayload(
            id="alter_A", branch_ref="branch_A",
            source_refs={
                "snapshot_ref": "alters/current/snapshot.yaml",
                "branches_ref": "alters/current/branches.yaml",
                "rubric_ref": "alters/calibration/rubric.yaml",
            },
            quality_status={"human_confirmed": True, "active": True},
            voice={"core_stance": "Test"},
            time_horizon="1.5-2年后",
        )


def test_alter_persist_request_rejects_extra_fields():
    with pytest.raises(Exception):
        AlterPersistRequest(
            approval_token="test",
            provider={"name": "openai"},
        )


def test_alter_batch_persist_request_rejects_extra_fields():
    with pytest.raises(Exception):
        AlterBatchPersistRequest(
            approval_token="test",
            alters=[],
            database={"engine": "postgres"},
        )


# --- raw dict validation and write ---


def _valid_alter_raw_dict(alter_id: str = "alter_A") -> dict:
    branch_ref = alter_id.replace("alter_", "branch_")
    return {
        "id": alter_id,
        "branch_ref": branch_ref,
        "label": f"Test {alter_id}",
        "generated_at": "2026-05-19",
        "time_horizon": "1.5-2年后",
        "source_branch": {"core_choice": "test", "structural_commitment": "test", "key_tension_resolved": "test"},
        "life_state": {"daily_structure": "test", "primary_tension": "test", "social_context": "test", "dominant_environment": "test"},
        "source_refs": {
            "snapshot_ref": "alters/current/snapshot.yaml",
            "branches_ref": "alters/current/branches.yaml",
            "rubric_ref": "alters/calibration/rubric.yaml",
        },
        "quality_status": {"human_confirmed": True, "active": True, "notes": []},
        "voice": {"core_stance": "Test stance", "typical_concern": "", "decision_style": "", "self_warning": ""},
    }


def test_validate_alter_raw_dict_valid():
    result = validate_alter_raw_dict(_valid_alter_raw_dict())
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_alter_raw_dict_preserves_extra_fields():
    d = _valid_alter_raw_dict()
    d["time_horizon"] = "3-5年"
    d["personality_drift"] = {"risk_tolerance": {"direction": "↓", "reason": "test"}}
    result = validate_alter_raw_dict(d)
    assert result["valid"] is True


def test_validate_alter_raw_dict_rejects_forbidden_field():
    d = _valid_alter_raw_dict()
    d["dialogue"] = {"sessions": []}
    result = validate_alter_raw_dict(d)
    assert result["valid"] is False
    assert any("dialogue" in e for e in result["errors"])


def test_validate_alter_raw_dict_rejects_wrong_id():
    d = _valid_alter_raw_dict()
    d["id"] = "alter_E"
    result = validate_alter_raw_dict(d)
    assert result["valid"] is False


def test_write_alter_raw_batch_preserves_extra_fields(tmp_path):
    alters = [_valid_alter_raw_dict(f"alter_{c}") for c in "ABCD"]
    audit_path = tmp_path / "audit.jsonl"
    result = write_alter_raw_batch_with_audit(
        alters=alters,
        base_dir=tmp_path,
        audit_log_path=audit_path,
        approval_token="test-token-123",
        caller="test",
        create_backup=False,
    )
    assert result["status"] == "persisted"
    for c in "ABCD":
        alter_file = tmp_path / f"alter_{c}.yaml"
        assert alter_file.exists()
        content = alter_file.read_text()
        assert "time_horizon" in content
        assert "source_branch" in content
        assert "life_state" in content
