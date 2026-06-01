"""Behavior metrics storage service."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.behavior_metrics_catalog import (
    load_catalog,
    load_known_metric_ids,
)
from alters_lab.schemas.behavior_metrics_record import (
    WeeklyBehaviorMetricsRecord,
    validate_missing_metric_ids,
)
from alters_lab.schemas.branch_milestones import BranchMilestoneRecord
from alters_lab.services.p6_runtime import (
    generate_record_id,
    list_records,
    read_record,
    utc_now,
    write_record,
)


def build_weekly_record(
    record: WeeklyBehaviorMetricsRecord,
    repo_root: Path | None = None,
) -> WeeklyBehaviorMetricsRecord:
    """Validate catalog constraints and return the record ready for saving."""
    catalog_path = _resolve_catalog_path(repo_root)
    known_ids = load_known_metric_ids(catalog_path)
    validate_missing_metric_ids(record, known_ids)
    return record


def save_weekly_record(
    record: WeeklyBehaviorMetricsRecord,
    repo_root: Path | None = None,
) -> Path:
    data = record.model_dump()
    data["week_start"] = str(data["week_start"])
    data["week_end"] = str(data["week_end"])
    return write_record("behavior_metrics", record.record_id, data, repo_root)


def load_weekly_record(
    record_id: str,
    repo_root: Path | None = None,
) -> WeeklyBehaviorMetricsRecord:
    data = read_record("behavior_metrics", record_id, repo_root)
    return WeeklyBehaviorMetricsRecord(**data)


def list_weekly_records(
    repo_root: Path | None = None,
) -> list[WeeklyBehaviorMetricsRecord]:
    return [
        WeeklyBehaviorMetricsRecord(**r)
        for r in list_records("behavior_metrics", repo_root)
    ]


def validate_milestone_reference(
    record: WeeklyBehaviorMetricsRecord,
    repo_root: Path | None = None,
) -> None:
    """Validate milestone_id references an existing milestone with matching branch_id."""
    if not record.milestone_id:
        return

    from alters_lab.services.branch_milestones import load_milestone

    try:
        milestone = load_milestone(record.milestone_id, repo_root)
    except FileNotFoundError as exc:
        raise ValueError(
            f"milestone_id '{record.milestone_id}' does not exist"
        ) from exc

    if record.branch_id and milestone.branch_id != record.branch_id:
        raise ValueError(
            f"branch_id mismatch: record has '{record.branch_id}', "
            f"milestone has '{milestone.branch_id}'"
        )


def _resolve_catalog_path(repo_root: Path | None) -> Path | None:
    if repo_root is None:
        return None
    return (
        repo_root
        / "alters"
        / "product"
        / "behavior_metrics"
        / "catalog"
        / "behavior_metric_set_v0_2.yaml"
    )
