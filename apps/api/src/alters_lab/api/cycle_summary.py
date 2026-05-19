from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.loaders import (
    default_project_root,
    load_active_yaml_chain,
    summarize_active_yaml_chain,
    validate_active_yaml_chain,
)
from alters_lab.loaders.active_yaml import active_yaml_paths
from alters_lab.schemas.cycle_summary import (
    ArtifactInfo,
    ArtifactListResponse,
    BoundaryConfirmations,
    CycleSummaryData,
    CycleSummaryHealthResponse,
    CycleSummaryResponse,
    ValidationErrorDetail,
    ValidationResponse,
)

router = APIRouter(prefix="/cycle-summary", tags=["cycle-summary"])


def _artifact_metadata(project_root: Path | None = None) -> list[dict]:
    paths = active_yaml_paths(project_root)
    date = "2026-05-19"
    entries = [
        ("snapshot", paths.snapshot),
        ("branches", paths.branches),
        ("alter_A", paths.alters["alter_A"]),
        ("alter_B", paths.alters["alter_B"]),
        ("alter_C", paths.alters["alter_C"]),
        ("alter_D", paths.alters["alter_D"]),
        ("value_alignment", paths.value_alignment),
        ("dialogue", paths.dialogue),
        ("reality_trace", paths.reality_trace),
    ]
    return [
        {"key": key, "path": str(path.relative_to(project_root or default_project_root())), "exists": path.exists()}
        for key, path in entries
    ]


@router.get("/health", response_model=CycleSummaryHealthResponse)
def health():
    return CycleSummaryHealthResponse()


@router.get("/current", response_model=CycleSummaryResponse)
def current():
    try:
        chain = load_active_yaml_chain()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "error_type": "active_yaml_load_failed", "message": str(exc)},
        )

    summary_data = summarize_active_yaml_chain(chain)
    validation_result = validate_active_yaml_chain(chain)

    return CycleSummaryResponse(
        summary=CycleSummaryData(**summary_data),
        validation=ValidationErrorDetail(
            ok=validation_result.ok,
            errors=validation_result.errors,
            warnings=validation_result.warnings,
        ),
        boundary_confirmations=BoundaryConfirmations(),
    )


@router.get("/validation", response_model=ValidationResponse)
def validation():
    try:
        chain = load_active_yaml_chain()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "error_type": "active_yaml_load_failed", "message": str(exc)},
        )

    result = validate_active_yaml_chain(chain)
    artifacts = _artifact_metadata()

    return ValidationResponse(
        status="PASS" if result.ok else "FAIL",
        ok=result.ok,
        errors=result.errors,
        warnings=result.warnings,
        artifacts_checked=len(artifacts),
    )


@router.get("/artifacts", response_model=ArtifactListResponse)
def artifacts():
    try:
        load_active_yaml_chain()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "error_type": "active_yaml_load_failed", "message": str(exc)},
        )

    metadata = _artifact_metadata()
    return ArtifactListResponse(
        artifacts=[ArtifactInfo(**a) for a in metadata],
        count=len(metadata),
    )
