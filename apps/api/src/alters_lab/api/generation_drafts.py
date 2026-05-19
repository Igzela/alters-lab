"""Controlled Generation Draft API endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.generation_drafts import (
    DraftListResponse,
    GenerationBoundaryConfirmations,
    GenerationDraftPackage,
    GenerationPreviewRequest,
    GenerationPreviewResponse,
)
from alters_lab.services.generation_drafts import (
    build_generation_draft_package,
    generation_boundary_confirmations,
    list_generation_drafts,
    save_generation_draft_package,
    validate_generation_inputs,
)

# Import at module level for monkeypatching in tests
from alters_lab.loaders.active_yaml import load_active_yaml_chain  # noqa: F401

router = APIRouter(prefix="/generation-drafts", tags=["generation-drafts"])


def get_generation_draft_workspace() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "alters/drafts"


def get_generation_draft_audit_log_path() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "docs/harness/phase3_generation_draft_audit.jsonl"


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "generation-drafts",
        "mode": "draft_only",
        "provider_used": False,
    }


@router.post(
    "/preview",
    response_model=GenerationPreviewResponse,
)
def preview_generation(body: GenerationPreviewRequest):
    # Load active chain via existing loader
    try:
        active_chain = load_active_yaml_chain()
    except Exception:
        active_chain = None

    if body.save_draft:
        if not body.approval_token:
            raise HTTPException(status_code=400, detail="approval_token required when save_draft=true")

        draft_pkg = build_generation_draft_package(
            active_chain, body.include_branches, body.include_alters,
        )
        workspace = get_generation_draft_workspace()
        audit_log = get_generation_draft_audit_log_path()
        result = save_generation_draft_package(
            draft_pkg, workspace, audit_log,
            body.approval_token, caller=body.caller,
        )
        return GenerationPreviewResponse(
            status=result["status"],
            draft_package=draft_pkg,
            draft_path=result["draft_path"],
            audit_log_path=result["audit_log_path"],
            boundary_confirmations=generation_boundary_confirmations(),
        )
    else:
        draft_pkg = build_generation_draft_package(
            active_chain, body.include_branches, body.include_alters,
        )
        return GenerationPreviewResponse(
            status="draft_generated",
            draft_package=draft_pkg,
            boundary_confirmations=generation_boundary_confirmations(),
        )


@router.get("/list", response_model=DraftListResponse)
def list_drafts():
    workspace = get_generation_draft_workspace()
    drafts = list_generation_drafts(workspace)
    return DraftListResponse(
        status="ok",
        drafts=drafts,
        count=len(drafts),
    )
