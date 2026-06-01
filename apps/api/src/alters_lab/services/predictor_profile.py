"""Predictor profile service — save/load structured baseline predictors."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.predictor_profile import PredictorProfileRecord
from alters_lab.services.p6_runtime import (
    list_records,
    read_record,
    write_record,
)

AREA = "predictor_profiles"


def save_profile(record: PredictorProfileRecord, repo_root: Path | None = None) -> Path:
    data = record.model_dump(mode="json")
    return write_record(AREA, record.profile_id, data, repo_root=repo_root)


def load_profile(profile_id: str, repo_root: Path | None = None) -> PredictorProfileRecord:
    data = read_record(AREA, profile_id, repo_root=repo_root)
    return PredictorProfileRecord(**data)


def list_profiles(repo_root: Path | None = None) -> list[PredictorProfileRecord]:
    records = list_records(AREA, repo_root=repo_root)
    return [PredictorProfileRecord(**r) for r in records]
