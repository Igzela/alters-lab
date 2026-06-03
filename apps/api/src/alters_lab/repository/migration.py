"""Migration utilities — move data between repository implementations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from alters_lab.repository.base import Repository
from alters_lab.repository.sqlite_repo import SqliteRepository
from alters_lab.repository.yaml_repo import YamlRepository
from alters_lab.services.p6_runtime import P6_RUNTIME_AREAS


MIGRATABLE_AREAS = [
    "forecast_snapshots",
    "external_evidence",
    "forecast_evaluations",
    "model_cards",
    "population_prior_artifacts",
    "predictor_profiles",
    "branch_outcome_targets",
    "behavior_metrics",
    "calibration_records",
    "pattern_reviews",
    "weekly_reviews",
    "weekly_notes",
    "branch_milestones",
]


def migrate_yaml_to_sqlite(
    yaml_repo: YamlRepository,
    sqlite_repo: SqliteRepository,
    areas: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, int]:
    """Migrate data from YAML repo to SQLite repo.

    Args:
        yaml_repo: Source YAML repository
        sqlite_repo: Target SQLite repository
        areas: List of areas to migrate (default: MIGRATABLE_AREAS)
        dry_run: If True, only count records without writing

    Returns:
        Dict mapping area name to number of records migrated (or counted).
    """
    target_areas = areas or MIGRATABLE_AREAS
    results: dict[str, int] = {}

    for area in target_areas:
        records = yaml_repo.list_records(area)
        count = len(records)
        if not dry_run and count > 0:
            for record in records:
                record_id = _extract_record_id(area, record)
                if record_id:
                    sqlite_repo.write(area, record_id, record)
        results[area] = count

    return results


def migrate_sqlite_to_yaml(
    sqlite_repo: SqliteRepository,
    yaml_repo: YamlRepository,
    areas: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, int]:
    """Migrate data from SQLite repo to YAML repo.

    Args:
        sqlite_repo: Source SQLite repository
        yaml_repo: Target YAML repository
        areas: List of areas to migrate (default: MIGRATABLE_AREAS)
        dry_run: If True, only count records without writing

    Returns:
        Dict mapping area name to number of records migrated (or counted).
    """
    target_areas = areas or MIGRATABLE_AREAS
    results: dict[str, int] = {}

    for area in target_areas:
        records = sqlite_repo.list_records(area)
        count = len(records)
        if not dry_run and count > 0:
            for record in records:
                record_id = _extract_record_id(area, record)
                if record_id:
                    yaml_repo.write(area, record_id, record)
        results[area] = count

    return results


def dry_run_migration(
    source: Repository,
    areas: list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Preview migration without writing. Returns per-area stats.

    Returns:
        Dict mapping area to {count, sample_ids: [...]}
    """
    target_areas = areas or MIGRATABLE_AREAS
    result: dict[str, dict[str, Any]] = {}

    for area in target_areas:
        records = source.list_records(area)
        sample_ids = []
        for r in records[:3]:
            rid = _extract_record_id(area, r)
            if rid:
                sample_ids.append(rid)
        result[area] = {
            "count": len(records),
            "sample_ids": sample_ids,
        }

    return result


def _extract_record_id(area: str, record: dict[str, Any]) -> str | None:
    """Extract a record ID from a record dict based on area conventions."""
    # Try common ID field patterns
    for key in [
        f"{area.rstrip('s')}_id",
        "snapshot_id",
        "evidence_id",
        "evaluation_id",
        "model_id",
        "artifact_id",
        "profile_id",
        "target_id",
        "record_id",
        "review_id",
        "milestone_id",
        "session_id",
    ]:
        if key in record and record[key]:
            return str(record[key])
    return None
