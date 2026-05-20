"""Tests for Alter Dialogue Runtime service (P4-M1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from alters_lab.schemas.alter_dialogue import (
    AlterDialogueBoundaryConfirmations,
    AlterDialogueContext,
    AlterDialoguePromptPacket,
    AlterDialogueRequest,
    AlterDialogueResponse,
)
from alters_lab.services.alter_dialogue import (
    alter_dialogue_boundary_confirmations,
    build_alter_dialogue_context,
    build_dialogue_response,
    build_prompt_packet,
    build_system_instruction,
    get_repo_root,
    list_active_alters,
    load_active_alter,
    validate_active_alter_for_dialogue,
    validate_alter_id,
)


def test_boundary_confirmations_read_only():
    bc = alter_dialogue_boundary_confirmations()
    assert bc["read_only"] is True
    assert bc["active_yaml_modified"] is False
    assert bc["dialogue_persisted_to_active"] is False
    assert bc["provider_used"] is False
    assert bc["provider_config_added"] is False
    assert bc["frontend_added"] is False
    assert bc["database_added"] is False
    assert bc["controlled_persist_called"] is False
    assert bc["live_execution_called"] is False
    assert bc["reality_score_created"] is False
    assert bc["drift_computed"] is False
    assert bc["calibration_modified"] is False
    assert bc["archive_created"] is False


def test_validate_alter_id_accepts_valid():
    for aid in ["alter_A", "alter_B", "alter_C", "alter_D"]:
        validate_alter_id(aid)


def test_validate_alter_id_rejects_path_traversal():
    with pytest.raises(ValueError):
        validate_alter_id("alter_A/../etc/passwd")
    with pytest.raises(ValueError):
        validate_alter_id("alter_A\\..\\secret")


def test_validate_alter_id_rejects_invalid():
    with pytest.raises(ValueError):
        validate_alter_id("alter_E")
    with pytest.raises(ValueError):
        validate_alter_id("")
    with pytest.raises(ValueError):
        validate_alter_id("not_alter")


def test_get_repo_root():
    root = get_repo_root()
    assert root.exists()
    assert (root / "apps").exists()


def test_load_active_alter():
    alter = load_active_alter("alter_A")
    assert alter["id"] == "alter_A"
    assert alter["branch_ref"] == "branch_A"
    assert "voice" in alter
    assert "quality_status" in alter


def test_load_active_alter_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_active_alter("alter_A", tmp_path)


VALID_ALTER = {
    "id": "alter_A",
    "branch_ref": "branch_A",
    "label": "Test Alter",
    "voice": {"core_stance": "Test stance"},
    "source_refs": {
        "snapshot_ref": "alters/current/snapshot.yaml",
        "branches_ref": "alters/current/branches.yaml",
        "rubric_ref": "alters/calibration/rubric.yaml",
    },
    "quality_status": {
        "human_confirmed": True,
        "active": True,
    },
}


def test_validate_active_alter_for_dialogue_valid():
    result = validate_active_alter_for_dialogue(VALID_ALTER)
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_active_alter_wrong_branch_ref():
    alter = {**VALID_ALTER, "branch_ref": "branch_X"}
    result = validate_active_alter_for_dialogue(alter)
    assert result["valid"] is False
    assert any("branch_ref mismatch" in e for e in result["errors"])


def test_validate_active_alter_bad_source_refs():
    alter = {**VALID_ALTER, "source_refs": {"snapshot_ref": "wrong"}}
    result = validate_active_alter_for_dialogue(alter)
    assert result["valid"] is False
    assert any("snapshot_ref" in e for e in result["errors"])


def test_validate_active_alter_inactive():
    alter = {**VALID_ALTER, "quality_status": {"active": False, "human_confirmed": True}}
    result = validate_active_alter_for_dialogue(alter)
    assert result["valid"] is False
    assert any("active" in e for e in result["errors"])


def test_validate_active_alter_not_human_confirmed():
    alter = {**VALID_ALTER, "quality_status": {"active": True, "human_confirmed": False}}
    result = validate_active_alter_for_dialogue(alter)
    assert result["valid"] is False
    assert any("human_confirmed" in e for e in result["errors"])


def test_validate_active_alter_missing_voice():
    alter = {**VALID_ALTER, "voice": {}}
    result = validate_active_alter_for_dialogue(alter)
    assert result["valid"] is False
    assert any("core_stance" in e for e in result["errors"])


def test_validate_active_alter_forbidden_field():
    alter = {**VALID_ALTER, "provider": "openai"}
    result = validate_active_alter_for_dialogue(alter)
    assert result["valid"] is False
    assert any("Forbidden" in e and "provider" in e for e in result["errors"])


def test_build_alter_dialogue_context():
    context = build_alter_dialogue_context(VALID_ALTER)
    assert isinstance(context, AlterDialogueContext)
    assert context.alter_id == "alter_A"
    assert context.core_stance == "Test stance"
    assert len(context.allowed_scope) > 0
    assert len(context.forbidden_scope) > 0


def test_build_system_instruction():
    context = build_alter_dialogue_context(VALID_ALTER)
    instruction = build_system_instruction(context)
    assert "alter_A" in instruction
    assert "read-only" in instruction.lower() or "read_only" in instruction.lower()
    assert "Test stance" in instruction
    assert "full alter YAML" in instruction


def test_build_prompt_packet():
    packet = build_prompt_packet(VALID_ALTER, "Hello alter")
    assert isinstance(packet, AlterDialoguePromptPacket)
    assert packet.alter_id == "alter_A"
    assert packet.provider_ready is False
    assert packet.full_context_injected is True
    assert packet.context_injection_policy == "full_alter_yaml_required"
    assert packet.full_alter_yaml == VALID_ALTER
    assert packet.full_alter_yaml["source_refs"]["rubric_ref"] == "alters/calibration/rubric.yaml"
    assert packet.persistence_policy == "read_only_no_active_yaml_write"
    assert "Hello alter" in packet.user_message


def test_build_prompt_packet_invalid_alter():
    bad_alter = {**VALID_ALTER, "voice": {}}
    with pytest.raises(ValueError):
        build_prompt_packet(bad_alter, "test")


def test_list_active_alters():
    alters = list_active_alters()
    assert len(alters) == 4
    ids = {a["alter_id"] for a in alters}
    assert ids == {"alter_A", "alter_B", "alter_C", "alter_D"}
    for a in alters:
        assert "label" in a
        assert "core_stance" in a
        assert "active" in a
        assert "human_confirmed" in a


def test_list_active_alters_returns_metadata_only():
    alters = list_active_alters()
    for a in alters:
        assert "source_branch" not in a
        assert "life_state" not in a
        assert "tradeoffs" not in a
        assert "personality_drift" not in a
        assert "value_alignment" not in a


def test_build_dialogue_response():
    request = AlterDialogueRequest(user_message="Hello alter")
    response = build_dialogue_response("alter_A", request)
    assert isinstance(response, AlterDialogueResponse)
    assert response.status == "prompt_packet_ready"
    assert response.alter_id == "alter_A"
    assert response.prompt_packet is not None
    assert response.prompt_packet.provider_ready is False
    assert response.dialogue_context is not None
    assert response.boundary_confirmations["read_only"] is True


def test_build_dialogue_response_no_context():
    request = AlterDialogueRequest(user_message="Hello", include_context_packet=False)
    response = build_dialogue_response("alter_A", request)
    assert response.status == "context_ready"
    assert response.prompt_packet is None
    assert response.dialogue_context is not None


def test_build_dialogue_response_invalid_alter():
    request = AlterDialogueRequest(user_message="Hello")
    with pytest.raises(ValueError):
        build_dialogue_response("alter_E", request)


def test_build_dialogue_response_rejected_validation():
    request = AlterDialogueRequest(user_message="Hello")
    # Monkeypatch a bad alter
    import alters_lab.services.alter_dialogue as svc
    original_load = svc.load_active_alter

    def bad_load(alter_id, repo_root=None):
        return {**VALID_ALTER, "voice": {}}

    svc.load_active_alter = bad_load
    try:
        response = build_dialogue_response("alter_A", request)
        assert response.status == "rejected"
    finally:
        svc.load_active_alter = original_load


def test_request_validation_rejects_empty():
    with pytest.raises(Exception):
        AlterDialogueRequest(user_message="")


def test_request_validation_rejects_long():
    with pytest.raises(Exception):
        AlterDialogueRequest(user_message="x" * 4001)


def test_schema_extra_forbid():
    with pytest.raises(Exception):
        AlterDialogueBoundaryConfirmations(evil_field=True)
    with pytest.raises(Exception):
        AlterDialogueContext(
            alter_id="x", branch_ref="x", label="x", core_stance="x",
            source_refs={}, quality_status={}, allowed_scope=[], forbidden_scope=[],
            evil_field=True,
        )
