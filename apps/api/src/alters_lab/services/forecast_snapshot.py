"""Forecast snapshot service — save/load locked forecast snapshots."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.forecast_snapshot import ForecastSnapshotRecord
from alters_lab.services.p6_runtime import (
    list_records,
    read_record,
    write_record,
)

AREA = "forecast_snapshots"


def save_snapshot(record: ForecastSnapshotRecord, repo_root: Path | None = None) -> Path:
    data = record.model_dump(mode="json")
    return write_record(AREA, record.snapshot_id, data, repo_root=repo_root)


def load_snapshot(snapshot_id: str, repo_root: Path | None = None) -> ForecastSnapshotRecord:
    data = read_record(AREA, snapshot_id, repo_root=repo_root)
    return ForecastSnapshotRecord(**data)


def list_snapshots(repo_root: Path | None = None) -> list[ForecastSnapshotRecord]:
    records = list_records(AREA, repo_root=repo_root)
    return [ForecastSnapshotRecord(**r) for r in records]


def list_snapshots_for_branch(branch_id: str, repo_root: Path | None = None) -> list[ForecastSnapshotRecord]:
    return [s for s in list_snapshots(repo_root=repo_root) if s.branch_id == branch_id]
