"""Service tests for draft review and promotion boundary."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from alters_lab.schemas.draft_review import (
    DraftReviewBoundaryConfirmations,
    DraftReviewDecision,
    DraftReviewRequest,
    PromotionPackage,
)
from alters_lab.services.draft_review import (
    build_alters_promotion_payload,
    build_branches_promotion_payload,
    build_promotion_package,
    create_review_decision,
    draft_review_boundary_confirmations,
    list_draft_reviews,
    load_draft_package,
    save_promotion_package,
    save_review_decision,
    validate_draft_package_for_review,
)


def _valid_draft_package() -> dict:
    return {
        "draft_id": "draft_test_001",
        "status": "draft",
        "active_write_allowed": False,
        "human_review_required": True,
        "generator": {"provider_used": False, "deterministic": True, "mode": "draft_only", "version": "1.0"},
        "boundary_confirmations": {"draft_only": True, "active_yaml_modified": False},
        "branch_drafts": [
            {"id": f"branch_{c}", "label": f"Branch {c}", "draft_status": "candidate", "requires_human_review": True,
             "core_choice": "x", "structural_commitment": "x", "key_tension_resolved": "x",
             "incompatible_with": [f"branch_{x}" for x in "ABCD" if x != c], "source_reasoning": ["reason"]}
            for c in "ABCD"
        ],
        "alter_drafts": [
            {"id": f"alter_{c}", "branch_ref": f"branch_{c}", "label": f"Alter {c}",
             "draft_status": "candidate", "requires_human_review": True,
             "quality_status": {"human_confirmed": False, "active": False},
             "source_refs": {}, "voice": {"core_stance": "focused"}}
            for c in "ABCD"
        ],
    }


def _write_draft(workspace: Path, draft_id: str, pkg: dict):
    d = workspace / draft_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "draft_package.yaml").write_text(yaml.dump(pkg), encoding="utf-8")


# --- boundary confirmations ---


def test_boundary_confirmations_all_false():
    bc = draft_review_boundary_confirmations()
    assert bc["draft_only"] is True
    assert bc["active_yaml_modified"] is False
    assert bc["active_persist_triggered"] is False
    assert bc["draft_promoted_to_active"] is False
    assert bc["provider_used"] is False


# --- load_draft_package ---


def test_load_draft_package(tmp_path):
    _write_draft(tmp_path, "draft_001", _valid_draft_package())
    pkg = load_draft_package(tmp_path, "draft_001")
    assert pkg["draft_id"] == "draft_test_001"
    assert pkg["status"] == "draft"


def test_load_draft_package_rejects_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_draft_package(tmp_path, "nonexistent")


def test_load_draft_package_rejects_path_traversal(tmp_path):
    with pytest.raises(ValueError, match="path traversal"):
        load_draft_package(tmp_path, "../etc/passwd")


def test_load_draft_package_rejects_backslash(tmp_path):
    with pytest.raises(ValueError, match="path traversal"):
        load_draft_package(tmp_path, "draft\\..\\secret")


# --- validate_draft_package_for_review ---


def test_validate_draft_package_passes():
    result = validate_draft_package_for_review(_valid_draft_package())
    assert result["valid"] is True


def test_validate_draft_package_rejects_active_write():
    pkg = _valid_draft_package()
    pkg["active_write_allowed"] = True
    result = validate_draft_package_for_review(pkg)
    assert result["valid"] is False
    assert any("active_write_allowed" in e for e in result["errors"])


def test_validate_draft_package_rejects_provider_used():
    pkg = _valid_draft_package()
    pkg["generator"]["provider_used"] = True
    result = validate_draft_package_for_review(pkg)
    assert result["valid"] is False
    assert any("provider_used" in e for e in result["errors"])


def test_validate_draft_package_rejects_no_human_review():
    pkg = _valid_draft_package()
    pkg["human_review_required"] = False
    result = validate_draft_package_for_review(pkg)
    assert result["valid"] is False
    assert any("human_review_required" in e for e in result["errors"])


def test_validate_draft_package_rejects_alter_active():
    pkg = _valid_draft_package()
    pkg["alter_drafts"][0]["quality_status"]["active"] = True
    result = validate_draft_package_for_review(pkg)
    assert result["valid"] is False
    assert any("active" in e for e in result["errors"])


def test_validate_draft_package_rejects_no_drafts():
    pkg = _valid_draft_package()
    pkg["branch_drafts"] = []
    pkg["alter_drafts"] = []
    result = validate_draft_package_for_review(pkg)
    assert result["valid"] is False
    assert any("no branch_drafts" in e for e in result["errors"])


# --- create_review_decision ---


def test_create_review_decision_approve():
    req = DraftReviewRequest(
        decision="approve_for_promotion_package",
        approved_branch_ids=["branch_A", "branch_B", "branch_C", "branch_D"],
        approved_alter_ids=["alter_A", "alter_B", "alter_C", "alter_D"],
    )
    decision = create_review_decision("draft_001", req)
    assert decision.decision == "approve_for_promotion_package"
    assert decision.created_at != ""
    assert decision.boundary_confirmations.draft_only is True


def test_create_review_decision_reject_approve_no_ids():
    req = DraftReviewRequest(decision="approve_for_promotion_package")
    with pytest.raises(ValueError, match="at least one"):
        create_review_decision("draft_001", req)


def test_create_review_decision_request_changes():
    req = DraftReviewRequest(decision="request_changes", notes=["need more detail"])
    decision = create_review_decision("draft_001", req)
    assert decision.decision == "request_changes"


def test_create_review_decision_reject_with_notes():
    req = DraftReviewRequest(decision="reject", notes=["not suitable"])
    decision = create_review_decision("draft_001", req)
    assert decision.decision == "reject"


def test_create_review_decision_reject_without_notes():
    req = DraftReviewRequest(decision="reject")
    with pytest.raises(ValueError, match="notes"):
        create_review_decision("draft_001", req)


# --- build_branches_promotion_payload ---


def test_build_branches_payload():
    pkg = _valid_draft_package()
    payload = build_branches_promotion_payload(pkg, ["branch_A", "branch_B", "branch_C", "branch_D"])
    assert payload["branch_discovery"]["status"] == "completed"
    assert len(payload["branches"]) == 4


def test_build_branches_payload_rejects_incomplete():
    pkg = _valid_draft_package()
    with pytest.raises(ValueError, match="Exactly branch_A-D"):
        build_branches_promotion_payload(pkg, ["branch_A", "branch_B"])


# --- build_alters_promotion_payload ---


def test_build_alters_payload():
    pkg = _valid_draft_package()
    payload = build_alters_promotion_payload(pkg, ["alter_A", "alter_B", "alter_C", "alter_D"])
    assert len(payload["alters"]) == 4
    for a in payload["alters"]:
        assert a["quality_status"]["human_confirmed"] is True
        assert a["quality_status"]["active"] is True


def test_build_alters_payload_rejects_incomplete():
    pkg = _valid_draft_package()
    with pytest.raises(ValueError, match="Exactly alter_A-D"):
        build_alters_promotion_payload(pkg, ["alter_A"])


# --- build_promotion_package ---


def test_build_promotion_package_both():
    pkg = _valid_draft_package()
    decision = DraftReviewDecision(
        draft_id="draft_test_001",
        decision="approve_for_promotion_package",
        approved_branch_ids=["branch_A", "branch_B", "branch_C", "branch_D"],
        approved_alter_ids=["alter_A", "alter_B", "alter_C", "alter_D"],
    )
    promo = build_promotion_package(pkg, decision)
    assert promo.status == "promotion_candidate"
    assert promo.active_write_allowed is False
    assert promo.requires_controlled_persist_api is True
    assert "/branches/persist" in promo.target_persist_apis
    assert "/alters/persist-batch" in promo.target_persist_apis


def test_build_promotion_package_branches_only():
    pkg = _valid_draft_package()
    decision = DraftReviewDecision(
        draft_id="draft_test_001",
        decision="approve_for_promotion_package",
        approved_branch_ids=["branch_A", "branch_B", "branch_C", "branch_D"],
    )
    promo = build_promotion_package(pkg, decision)
    assert promo.branches_payload is not None
    assert promo.alters_payload is None
    assert promo.target_persist_apis == ["/branches/persist"]


def test_build_promotion_package_rejects_non_approve():
    pkg = _valid_draft_package()
    decision = DraftReviewDecision(
        draft_id="draft_test_001",
        decision="request_changes",
        notes=["fix"],
    )
    with pytest.raises(ValueError, match="approve"):
        build_promotion_package(pkg, decision)


# --- save_review_decision ---


def test_save_review_decision(tmp_path):
    decision = DraftReviewDecision(
        draft_id="draft_001",
        decision="request_changes",
        notes=["fix"],
    )
    result = save_review_decision(tmp_path, "draft_001", decision, "token-123")
    assert result["status"] == "review_saved"
    assert (tmp_path / "draft_001" / "review_decision.yaml").exists()


def test_save_review_decision_rejects_blank_token(tmp_path):
    decision = DraftReviewDecision(
        draft_id="draft_001",
        decision="reject",
        notes=["no"],
    )
    with pytest.raises(ValueError, match="approval_token"):
        save_review_decision(tmp_path, "draft_001", decision, "")


def test_save_review_no_raw_token(tmp_path):
    decision = DraftReviewDecision(
        draft_id="draft_001",
        decision="reject",
        notes=["no"],
    )
    save_review_decision(tmp_path, "draft_001", decision, "secret-token")
    content = (tmp_path / "draft_001" / "review_decision.yaml").read_text()
    assert "secret-token" not in content


# --- save_promotion_package ---


def test_save_promotion_package(tmp_path):
    decision = DraftReviewDecision(
        draft_id="draft_001",
        decision="approve_for_promotion_package",
        approved_branch_ids=["branch_A", "branch_B", "branch_C", "branch_D"],
    )
    pkg = _valid_draft_package()
    promo = build_promotion_package(pkg, decision)
    result = save_promotion_package(tmp_path, "draft_001", promo, "token-456")
    assert result["status"] == "promotion_package_saved"
    assert (tmp_path / "draft_001" / "promotion_package.yaml").exists()


def test_save_promotion_package_rejects_blank_token(tmp_path):
    decision = DraftReviewDecision(
        draft_id="draft_001",
        decision="approve_for_promotion_package",
        approved_branch_ids=["branch_A", "branch_B", "branch_C", "branch_D"],
    )
    pkg = _valid_draft_package()
    promo = build_promotion_package(pkg, decision)
    with pytest.raises(ValueError, match="approval_token"):
        save_promotion_package(tmp_path, "draft_001", promo, "")


def test_save_promotion_no_raw_token(tmp_path):
    decision = DraftReviewDecision(
        draft_id="draft_001",
        decision="approve_for_promotion_package",
        approved_branch_ids=["branch_A", "branch_B", "branch_C", "branch_D"],
    )
    pkg = _valid_draft_package()
    promo = build_promotion_package(pkg, decision)
    save_promotion_package(tmp_path, "draft_001", promo, "secret-token")
    content = (tmp_path / "draft_001" / "promotion_package.yaml").read_text()
    assert "secret-token" not in content


# --- list_draft_reviews ---


def test_list_draft_reviews_empty(tmp_path):
    reviews = list_draft_reviews(tmp_path / "nonexistent")
    assert reviews == []


def test_list_draft_reviews_metadata_only(tmp_path):
    _write_draft(tmp_path, "draft_001", _valid_draft_package())
    decision = DraftReviewDecision(
        draft_id="draft_001",
        decision="reject",
        notes=["no"],
    )
    save_review_decision(tmp_path, "draft_001", decision, "token")
    reviews = list_draft_reviews(tmp_path)
    assert len(reviews) == 1
    assert reviews[0]["review_exists"] is True
    assert reviews[0]["promotion_package_exists"] is False
    assert "branch_A" not in str(reviews[0])


# --- extra field rejection ---


def test_draft_review_request_rejects_extra():
    with pytest.raises(Exception):
        DraftReviewRequest(decision="reject", provider={"name": "openai"})


def test_draft_review_decision_rejects_extra():
    with pytest.raises(Exception):
        DraftReviewDecision(draft_id="x", decision="reject", notes=["n"], runtime=True)
