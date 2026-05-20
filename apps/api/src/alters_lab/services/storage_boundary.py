"""P5-M5 Durable Storage Boundary service.

YAML remains default. Describes storage boundaries without adding a database.
No active writes.
"""

from __future__ import annotations

from alters_lab.schemas.storage_boundary import (
    StorageBoundaryHealthResponse,
    StorageManifestResponse,
)


def get_storage_boundary_health() -> StorageBoundaryHealthResponse:
    return StorageBoundaryHealthResponse()


def get_storage_manifest() -> StorageManifestResponse:
    return StorageManifestResponse(
        active_yaml_read_only=[
            "alters/current/snapshot.yaml",
            "alters/current/branches.yaml",
            "alters/current/alters/alter_A.yaml",
            "alters/current/alters/alter_B.yaml",
            "alters/current/alters/alter_C.yaml",
            "alters/current/alters/alter_D.yaml",
            "alters/current/reality_trace.yaml",
            "alters/current/value_alignment/*.yaml",
            "alters/current/dialogue/*.yaml",
        ],
        calibration_score_write=[
            "alters/calibration/scores/",
        ],
        product_session_write=[
            "alters/product/sessions/",
            "alters/product/provider_runs/",
            "alters/product/workflow_runs/",
            "alters/product/weekly_notes/",
            "alters/product/weekly_reviews/",
            "alters/product/calibration_records/",
            "alters/product/self_deception_challenges/",
            "alters/product/alter_recommendations/",
            "alters/product/reminders/",
            "alters/product/pattern_reviews/",
            "alters/product/exports/",
            "alters/product/behavior_validation/",
        ],
        ignored_runtime_areas=[
            "alters/product/sessions/",
            "alters/product/provider_runs/",
            "alters/product/workflow_runs/",
            "alters/product/weekly_notes/",
            "alters/product/weekly_reviews/",
            "alters/product/calibration_records/",
            "alters/product/self_deception_challenges/",
            "alters/product/alter_recommendations/",
            "alters/product/reminders/",
            "alters/product/pattern_reviews/",
            "alters/product/exports/",
            "alters/product/behavior_validation/",
        ],
        evidence_areas=[
            "docs/harness/P5_FINAL_EVIDENCE.json",
            "docs/harness/PHASE5_CLOSEOUT_REPORT.md",
            "docs/harness/PHASE5_CLOSEOUT_EVIDENCE.json",
            "alters/calibration/scores/",
        ],
    )
