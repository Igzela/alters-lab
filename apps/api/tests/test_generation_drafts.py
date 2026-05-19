"""Service tests for generation draft runtime."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from alters_lab.schemas.generation_drafts import (
    AlterDraftCandidate,
    BranchDraftCandidate,
    GenerationDraftPackage,
    GenerationPreviewRequest,
)
from alters_lab.loaders.models import ActiveYamlChain
from alters_lab.services.generation_drafts import (
    build_generation_draft_package,
    extract_branch_list,
    extract_snapshot_body,
    generate_alter_drafts_from_branches,
    generate_branch_drafts_from_snapshot,
    generation_boundary_confirmations,
    generate_draft_id,
    list_generation_drafts,
    normalize_active_chain,
    preview_generation_draft,
    save_generation_draft_package,
    validate_generation_inputs,
)
from alters_lab.services.controlled_write import sha256_text


def _minimal_active_chain() -> dict:
    return {
        "snapshot": {
            "intake_status": {"phase": "completed"},
        },
        "branches": {
            "branches": [
                {"id": "branch_A"}, {"id": "branch_B"},
                {"id": "branch_C"}, {"id": "branch_D"},
            ],
        },
    }


# --- boundary confirmations ---


def test_boundary_confirmations_all_false_for_active_mutation():
    bc = generation_boundary_confirmations()
    assert bc["draft_only"] is True
    assert bc["active_yaml_modified"] is False
    assert bc["provider_used"] is False
    assert bc["generation_promoted_to_active"] is False
    assert bc["active_persist_triggered"] is False


# --- validate_generation_inputs ---


def test_validate_inputs_passes():
    result = validate_generation_inputs(_minimal_active_chain())
    assert result["valid"] is True


def test_validate_inputs_rejects_none():
    result = validate_generation_inputs(None)
    assert result["valid"] is False


def test_validate_inputs_rejects_incomplete_snapshot():
    chain = {"snapshot": {"intake_status": {"phase": "not_started"}}}
    result = validate_generation_inputs(chain)
    assert result["valid"] is False


# --- branch draft generation ---


def test_branch_drafts_returns_exactly_four():
    drafts = generate_branch_drafts_from_snapshot({})
    assert len(drafts) == 4
    ids = {d.id for d in drafts}
    assert ids == {"branch_A", "branch_B", "branch_C", "branch_D"}


def test_branch_drafts_have_incompatible_with():
    drafts = generate_branch_drafts_from_snapshot({})
    for d in drafts:
        assert len(d.incompatible_with) == 3


def test_branch_drafts_require_human_review():
    drafts = generate_branch_drafts_from_snapshot({})
    for d in drafts:
        assert d.requires_human_review is True
        assert d.draft_status == "candidate"


# --- alter draft generation ---


def test_alter_drafts_returns_exactly_four():
    drafts = generate_alter_drafts_from_branches([])
    assert len(drafts) == 4
    ids = {d.id for d in drafts}
    assert ids == {"alter_A", "alter_B", "alter_C", "alter_D"}


def test_alter_drafts_map_to_branches():
    drafts = generate_alter_drafts_from_branches([])
    for d in drafts:
        expected_branch = d.id.replace("alter_", "branch_")
        assert d.branch_ref == expected_branch


def test_alter_drafts_not_human_confirmed():
    drafts = generate_alter_drafts_from_branches([])
    for d in drafts:
        assert d.quality_status["human_confirmed"] is False
        assert d.quality_status["active"] is False
        assert d.requires_human_review is True


# --- draft package ---


def test_draft_package_status_is_draft():
    pkg = build_generation_draft_package(_minimal_active_chain(), True, True)
    assert pkg.status == "draft"


def test_draft_package_active_write_not_allowed():
    pkg = build_generation_draft_package(_minimal_active_chain(), True, True)
    assert pkg.active_write_allowed is False
    assert pkg.human_review_required is True


def test_draft_package_provider_not_used():
    pkg = build_generation_draft_package(_minimal_active_chain(), True, True)
    assert pkg.generator.provider_used is False
    assert pkg.generator.deterministic is True


def test_draft_package_type_cycle():
    pkg = build_generation_draft_package(_minimal_active_chain(), True, True)
    assert pkg.draft_type == "cycle_package"


def test_draft_package_type_branches_only():
    pkg = build_generation_draft_package(_minimal_active_chain(), True, False)
    assert pkg.draft_type == "branches"


def test_draft_package_type_alters_only():
    pkg = build_generation_draft_package(_minimal_active_chain(), False, True)
    assert pkg.draft_type == "alters"


def test_draft_package_rejects_nothing():
    with pytest.raises(ValueError, match="At least one"):
        build_generation_draft_package(_minimal_active_chain(), False, False)


# --- preview ---


def test_preview_does_not_write(tmp_path):
    pkg = preview_generation_draft(_minimal_active_chain(), True, True)
    assert pkg.status == "draft"
    assert pkg.draft_type == "cycle_package"


# --- save ---


def test_save_writes_only_draft_workspace(tmp_path):
    pkg = build_generation_draft_package(_minimal_active_chain(), True, True)
    workspace = tmp_path / "drafts"
    audit = tmp_path / "audit.jsonl"
    result = save_generation_draft_package(pkg, workspace, audit, "test-token")
    assert result["status"] == "draft_saved"
    assert (workspace / pkg.draft_id / "draft_package.yaml").exists()


def test_save_audit_stores_hash_only(tmp_path):
    pkg = build_generation_draft_package(_minimal_active_chain(), True, True)
    workspace = tmp_path / "drafts"
    audit = tmp_path / "audit.jsonl"
    raw_token = "human-approval-token-123"
    save_generation_draft_package(pkg, workspace, audit, raw_token)
    content = audit.read_text()
    assert raw_token not in content
    assert sha256_text(raw_token) in content


def test_save_rejects_blank_token(tmp_path):
    pkg = build_generation_draft_package(_minimal_active_chain(), True, True)
    workspace = tmp_path / "drafts"
    audit = tmp_path / "audit.jsonl"
    with pytest.raises(ValueError, match="approval_token"):
        save_generation_draft_package(pkg, workspace, audit, "")


def test_save_audit_no_full_yaml(tmp_path):
    pkg = build_generation_draft_package(_minimal_active_chain(), True, True)
    workspace = tmp_path / "drafts"
    audit = tmp_path / "audit.jsonl"
    save_generation_draft_package(pkg, workspace, audit, "test-token")
    content = audit.read_text()
    assert "branch_A" not in content


# --- list ---


def test_list_empty_workspace(tmp_path):
    drafts = list_generation_drafts(tmp_path / "nonexistent")
    assert drafts == []


def test_list_returns_metadata_only(tmp_path):
    pkg = build_generation_draft_package(_minimal_active_chain(), True, True)
    workspace = tmp_path / "drafts"
    audit = tmp_path / "audit.jsonl"
    save_generation_draft_package(pkg, workspace, audit, "test-token")
    drafts = list_generation_drafts(workspace)
    assert len(drafts) == 1
    assert drafts[0]["draft_id"] == pkg.draft_id
    assert "branch_A" not in str(drafts[0])


# --- extra field rejection ---


def test_branch_draft_rejects_extra_fields():
    with pytest.raises(Exception):
        BranchDraftCandidate(id="branch_A", label="A", core_choice="c",
            structural_commitment="s", key_tension_resolved="t",
            incompatible_with=[], source_reasoning=[], runtime=True)


def test_alter_draft_rejects_extra_fields():
    with pytest.raises(Exception):
        AlterDraftCandidate(id="alter_A", branch_ref="branch_A", label="A",
            dialogue=True)


def test_draft_package_rejects_extra_fields():
    with pytest.raises(Exception):
        GenerationDraftPackage(draft_id="d1", draft_type="branches",
            provider={"name": "openai"})


def test_preview_request_rejects_extra_fields():
    with pytest.raises(Exception):
        GenerationPreviewRequest(calibration={"score": 0.9})


def test_preview_request_rejects_save_without_token():
    with pytest.raises(Exception):
        GenerationPreviewRequest(save_draft=True)


# --- normalize_active_chain ---


def test_normalize_active_chain_none():
    assert normalize_active_chain(None) == {}


def test_normalize_active_chain_dict():
    d = {"snapshot": {"a": 1}, "branches": {"b": 2}}
    assert normalize_active_chain(d) == d


def test_normalize_active_chain_dataclass():
    chain = ActiveYamlChain(
        snapshot={"snapshot": {"intake_status": {"phase": "completed"}}},
        branches={"branches": [{"id": "branch_A"}, {"id": "branch_B"}, {"id": "branch_C"}, {"id": "branch_D"}]},
        alters={"alter_A": {}, "alter_B": {}, "alter_C": {}, "alter_D": {}},
        value_alignment={},
        dialogue={},
        reality_trace={},
    )
    result = normalize_active_chain(chain)
    assert isinstance(result, dict)
    assert result["snapshot"]["snapshot"]["intake_status"]["phase"] == "completed"
    assert len(result["branches"]["branches"]) == 4


def test_normalize_active_chain_preserves_all_fields():
    chain = ActiveYamlChain(
        snapshot={"s": 1}, branches={"b": 2}, alters={"a": 3},
        value_alignment={"v": 4}, dialogue={"d": 5}, reality_trace={"r": 6},
    )
    result = normalize_active_chain(chain)
    assert set(result.keys()) == {"snapshot", "branches", "alters", "value_alignment", "dialogue", "reality_trace"}


# --- extract_snapshot_body ---


def test_extract_snapshot_body_wrapped():
    doc = {"snapshot": {"intake_status": {"phase": "completed"}, "anchors": {}}}
    body = extract_snapshot_body(doc)
    assert body["intake_status"]["phase"] == "completed"
    assert "snapshot" not in body


def test_extract_snapshot_body_unwrapped():
    doc = {"intake_status": {"phase": "completed"}, "anchors": {}}
    body = extract_snapshot_body(doc)
    assert body["intake_status"]["phase"] == "completed"


def test_extract_snapshot_body_empty():
    assert extract_snapshot_body({}) == {}


# --- extract_branch_list ---


def test_extract_branch_list_normal():
    doc = {"branches": [{"id": "branch_A"}, {"id": "branch_B"}]}
    assert len(extract_branch_list(doc)) == 2


def test_extract_branch_list_empty():
    assert extract_branch_list({}) == []


# --- validate with real wrapped snapshot ---


def test_validate_inputs_real_wrapped_snapshot():
    chain = {
        "snapshot": {
            "snapshot": {
                "intake_status": {"phase": "completed"},
                "anchors": {"heaviest_constraint": "x"},
            },
        },
        "branches": {
            "branches": [
                {"id": "branch_A"}, {"id": "branch_B"},
                {"id": "branch_C"}, {"id": "branch_D"},
            ],
        },
    }
    result = validate_generation_inputs(chain)
    assert result["valid"] is True


def test_validate_inputs_rejects_wrapped_snapshot_wrong_phase():
    chain = {
        "snapshot": {
            "snapshot": {
                "intake_status": {"phase": "not_started"},
            },
        },
    }
    result = validate_generation_inputs(chain)
    assert result["valid"] is False
    assert any("phase" in e for e in result["errors"])


# --- build with real ActiveYamlChain ---


def test_build_package_with_dataclass():
    chain = ActiveYamlChain(
        snapshot={
            "snapshot": {
                "intake_status": {"phase": "completed"},
                "anchors": {"heaviest_constraint": "x"},
            },
        },
        branches={
            "branches": [
                {"id": "branch_A"}, {"id": "branch_B"},
                {"id": "branch_C"}, {"id": "branch_D"},
            ],
        },
        alters={},
        value_alignment={},
        dialogue={},
        reality_trace={},
    )
    pkg = build_generation_draft_package(chain, True, True)
    assert pkg.status == "draft"
    assert len(pkg.branch_drafts) == 4
    assert len(pkg.alter_drafts) == 4
    assert pkg.active_write_allowed is False


def test_build_package_with_real_wrapped_dict():
    chain = {
        "snapshot": {
            "snapshot": {
                "intake_status": {"phase": "completed"},
            },
        },
        "branches": {
            "branches": [
                {"id": "branch_A"}, {"id": "branch_B"},
                {"id": "branch_C"}, {"id": "branch_D"},
            ],
        },
    }
    pkg = build_generation_draft_package(chain, True, False)
    assert len(pkg.branch_drafts) == 4
    assert len(pkg.alter_drafts) == 0
