"""Draft review and promotion boundary service."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from alters_lab.schemas.draft_review import (
    DraftReviewBoundaryConfirmations,
    DraftReviewDecision,
    DraftReviewRequest,
    PromotionAltersPayload,
    PromotionBranchesPayload,
    PromotionPackage,
)
from alters_lab.services.controlled_write import hash_approval_token


def draft_review_boundary_confirmations() -> dict:
    return DraftReviewBoundaryConfirmations().model_dump()


def load_draft_package(draft_workspace: Path, draft_id: str) -> dict:
    if "/" in draft_id or "\\" in draft_id or ".." in draft_id:
        raise ValueError(f"Invalid draft_id: path traversal detected")
    draft_path = draft_workspace / draft_id / "draft_package.yaml"
    if not draft_path.exists():
        raise FileNotFoundError(f"Draft package not found: {draft_path}")
    with open(draft_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid draft package format")
    return data


def validate_draft_package_for_review(draft_package: dict) -> dict:
    errors: list[str] = []

    if draft_package.get("status") != "draft":
        errors.append("status != 'draft'")
    if draft_package.get("active_write_allowed") is not False:
        errors.append("active_write_allowed != false")
    if draft_package.get("human_review_required") is not True:
        errors.append("human_review_required != true")

    generator = draft_package.get("generator", {})
    if generator.get("provider_used") is not False:
        errors.append("generator.provider_used != false")

    bc = draft_package.get("boundary_confirmations", {})
    if bc.get("draft_only") is not True:
        errors.append("boundary_confirmations.draft_only != true")
    if bc.get("active_yaml_modified") is not False:
        errors.append("boundary_confirmations.active_yaml_modified != false")

    branch_drafts = draft_package.get("branch_drafts", [])
    alter_drafts = draft_package.get("alter_drafts", [])
    if not branch_drafts and not alter_drafts:
        errors.append("no branch_drafts or alter_drafts")

    for bd in branch_drafts:
        if bd.get("draft_status") != "candidate":
            errors.append(f"branch {bd.get('id')}: draft_status != 'candidate'")
        if bd.get("requires_human_review") is not True:
            errors.append(f"branch {bd.get('id')}: requires_human_review != true")

    for ad in alter_drafts:
        if ad.get("draft_status") != "candidate":
            errors.append(f"alter {ad.get('id')}: draft_status != 'candidate'")
        if ad.get("requires_human_review") is not True:
            errors.append(f"alter {ad.get('id')}: requires_human_review != true")
        qs = ad.get("quality_status", {})
        if qs.get("human_confirmed") is not False:
            errors.append(f"alter {ad.get('id')}: quality_status.human_confirmed != false")
        if qs.get("active") is not False:
            errors.append(f"alter {ad.get('id')}: quality_status.active != false")

    return {"valid": len(errors) == 0, "errors": errors}


def create_review_decision(
    draft_id: str,
    request: DraftReviewRequest,
) -> DraftReviewDecision:
    return DraftReviewDecision(
        draft_id=draft_id,
        reviewer=request.reviewer,
        decision=request.decision,
        notes=request.notes,
        approved_branch_ids=request.approved_branch_ids,
        approved_alter_ids=request.approved_alter_ids,
        created_at=datetime.now(timezone.utc).isoformat(),
        boundary_confirmations=DraftReviewBoundaryConfirmations(),
    )


def build_branches_promotion_payload(
    draft_package: dict,
    approved_branch_ids: list[str],
) -> dict:
    expected = {"branch_A", "branch_B", "branch_C", "branch_D"}
    if set(approved_branch_ids) != expected:
        raise ValueError(f"Exactly branch_A-D required, got {approved_branch_ids}")

    branch_drafts = draft_package.get("branch_drafts", [])
    draft_ids = {b["id"] for b in branch_drafts}
    if draft_ids != expected:
        raise ValueError(f"Draft package missing branches: expected {expected}, found {draft_ids}")

    approved = [b for b in branch_drafts if b["id"] in approved_branch_ids]
    branches = []
    for b in approved:
        entry = {k: v for k, v in b.items() if k not in ("draft_status", "requires_human_review", "source_reasoning")}
        branches.append(entry)

    return {
        "branch_discovery": {
            "status": "completed",
            "source_snapshot_ref": "alters/current/snapshot.yaml",
            "confirmed_by": "human_owner",
            "confirmation_note": "promotion package candidate generated from reviewed draft",
        },
        "branches": branches,
    }


def build_alters_promotion_payload(
    draft_package: dict,
    approved_alter_ids: list[str],
) -> dict:
    expected = {"alter_A", "alter_B", "alter_C", "alter_D"}
    if set(approved_alter_ids) != expected:
        raise ValueError(f"Exactly alter_A-D required, got {approved_alter_ids}")

    alter_drafts = draft_package.get("alter_drafts", [])
    draft_ids = {a["id"] for a in alter_drafts}
    if draft_ids != expected:
        raise ValueError(f"Draft package missing alters: expected {expected}, found {draft_ids}")

    approved = [a for a in alter_drafts if a["id"] in approved_alter_ids]
    alters = []
    for a in approved:
        entry = {
            "id": a["id"],
            "branch_ref": a["branch_ref"],
            "label": a["label"],
            "source_refs": a.get("source_refs", {
                "snapshot_ref": "alters/current/snapshot.yaml",
                "branches_ref": "alters/current/branches.yaml",
                "rubric_ref": "alters/calibration/rubric.yaml",
            }),
            "quality_status": {
                "human_confirmed": True,
                "active": True,
            },
            "voice": a.get("voice", {}),
        }
        alters.append(entry)

    return {"alters": alters}


def build_promotion_package(
    draft_package: dict,
    review_decision: DraftReviewDecision,
) -> PromotionPackage:
    if review_decision.decision != "approve_for_promotion_package":
        raise ValueError("build_promotion_package requires approve_for_promotion_package decision")

    validation = validate_draft_package_for_review(draft_package)
    if not validation["valid"]:
        raise ValueError(f"Invalid draft package: {'; '.join(validation['errors'])}")

    branches_payload = None
    alters_payload = None
    target_apis = []

    if review_decision.approved_branch_ids:
        branches_payload = PromotionBranchesPayload(
            **build_branches_promotion_payload(draft_package, review_decision.approved_branch_ids)
        )
        target_apis.append("/branches/persist")

    if review_decision.approved_alter_ids:
        alters_payload = PromotionAltersPayload(
            **build_alters_promotion_payload(draft_package, review_decision.approved_alter_ids)
        )
        target_apis.append("/alters/persist-batch")

    return PromotionPackage(
        draft_id=draft_package["draft_id"],
        review_decision=review_decision,
        branches_payload=branches_payload,
        alters_payload=alters_payload,
        target_persist_apis=target_apis,
        boundary_confirmations=DraftReviewBoundaryConfirmations(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def save_review_decision(
    draft_workspace: Path,
    draft_id: str,
    review_decision: DraftReviewDecision,
    approval_token: str,
    caller: str = "api",
) -> dict:
    if not approval_token or not approval_token.strip():
        raise ValueError("approval_token must not be empty or whitespace-only")

    draft_dir = draft_workspace / draft_id
    draft_dir.mkdir(parents=True, exist_ok=True)
    review_path = draft_dir / "review_decision.yaml"

    content = yaml.dump(review_decision.model_dump(), default_flow_style=False, allow_unicode=True)
    review_path.write_text(content, encoding="utf-8")

    return {
        "status": "review_saved",
        "review_path": str(review_path),
        "approval_token_hash": hash_approval_token(approval_token),
    }


def save_promotion_package(
    draft_workspace: Path,
    draft_id: str,
    promotion_package: PromotionPackage,
    approval_token: str,
    caller: str = "api",
) -> dict:
    if not approval_token or not approval_token.strip():
        raise ValueError("approval_token must not be empty or whitespace-only")

    draft_dir = draft_workspace / draft_id
    draft_dir.mkdir(parents=True, exist_ok=True)
    promo_path = draft_dir / "promotion_package.yaml"

    content = yaml.dump(promotion_package.model_dump(), default_flow_style=False, allow_unicode=True)
    promo_path.write_text(content, encoding="utf-8")

    return {
        "status": "promotion_package_saved",
        "promotion_package_path": str(promo_path),
        "approval_token_hash": hash_approval_token(approval_token),
    }


def list_draft_reviews(draft_workspace: Path) -> list[dict]:
    if not draft_workspace.exists():
        return []
    reviews = []
    for d in sorted(draft_workspace.iterdir()):
        if d.is_dir() and d.name.startswith("draft_"):
            review_path = d / "review_decision.yaml"
            promo_path = d / "promotion_package.yaml"
            reviews.append({
                "draft_id": d.name,
                "review_exists": review_path.exists(),
                "promotion_package_exists": promo_path.exists(),
                "review_path": str(review_path),
                "promotion_package_path": str(promo_path),
            })
    return reviews
