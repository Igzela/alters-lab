"""Shared P6 runtime helpers.

P6 runtime records live under ignored product areas. These helpers deliberately
only read/write those areas and never touch active YAML or the calibration
rubric.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from alters_lab.services import io
from alters_lab.services.runtime_layout import RuntimeLayout, resolve_runtime_layout


P6_RUNTIME_AREAS = {
    "weekly_notes": "alters/product/weekly_notes",
    "weekly_reviews": "alters/product/weekly_reviews",
    "calibration_records": "alters/product/calibration_records",
    "self_deception_challenges": "alters/product/self_deception_challenges",
    "alter_recommendations": "alters/product/alter_recommendations",
    "reminders": "alters/product/reminders",
    "pattern_reviews": "alters/product/pattern_reviews",
    "exports": "alters/product/exports",
    "behavior_validation": "alters/product/behavior_validation",
    "behavior_metrics": "alters/product/behavior_metrics/weekly_records",
    "branch_milestones": "alters/product/branch_milestones",
    "predictor_profiles": "alters/product/predictor_profiles",
    "branch_outcome_targets": "alters/product/branch_outcome_targets",
    "forecast_snapshots": "alters/product/forecast_snapshots",
    "external_evidence": "alters/product/external_evidence",
    "forecast_evaluations": "alters/product/forecast_evaluations",
    "model_cards": "alters/product/model_cards",
    "population_prior_artifacts": "alters/product/population_prior_artifacts",
}

_SAFE_ID = re.compile(r"^[A-Za-z0-9_.-]+$")


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def compact_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def generate_record_id(prefix: str) -> str:
    return f"{prefix}_{compact_timestamp()}_{uuid.uuid4().hex[:8]}"


def validate_record_id(record_id: str) -> str:
    if not record_id or not _SAFE_ID.match(record_id) or ".." in record_id:
        raise ValueError(f"Invalid record id: {record_id}")
    return record_id


def runtime_dir(
    area: str,
    repo_root: Path | None = None,
    layout: RuntimeLayout | None = None,
    mode: str | None = None,
) -> Path:
    if area not in P6_RUNTIME_AREAS:
        raise ValueError(f"Unknown P6 runtime area: {area}")
    if repo_root is not None:
        return repo_root / P6_RUNTIME_AREAS[area]
    resolved_layout = layout or resolve_runtime_layout(mode=mode)
    if resolved_layout.mode == "packaged":
        return resolved_layout.product_data_dir / area
    root = resolved_layout.repo_root or get_repo_root()
    return root / P6_RUNTIME_AREAS[area]


def record_path(
    area: str,
    record_id: str,
    repo_root: Path | None = None,
    layout: RuntimeLayout | None = None,
    mode: str | None = None,
) -> Path:
    validate_record_id(record_id)
    return runtime_dir(area, repo_root, layout, mode) / f"{record_id}.yaml"


def write_record(
    area: str,
    record_id: str,
    data: dict[str, Any],
    repo_root: Path | None = None,
    layout: RuntimeLayout | None = None,
    mode: str | None = None,
) -> Path:
    path = record_path(area, record_id, repo_root, layout, mode)
    io.write_yaml(path, data)
    return path


def read_record(
    area: str,
    record_id: str,
    repo_root: Path | None = None,
    layout: RuntimeLayout | None = None,
    mode: str | None = None,
) -> dict[str, Any]:
    path = record_path(area, record_id, repo_root, layout, mode)
    if not path.exists():
        raise FileNotFoundError(f"P6 record not found: {record_id}")
    data = io.read_yaml(path)
    if not isinstance(data, dict):
        raise ValueError(f"P6 record is not a mapping: {record_id}")
    return data


def list_records(
    area: str,
    repo_root: Path | None = None,
    layout: RuntimeLayout | None = None,
    mode: str | None = None,
) -> list[dict[str, Any]]:
    directory = runtime_dir(area, repo_root, layout, mode)
    if not directory.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.yaml")):
        if path.name.startswith("_template"):
            continue
        data = io.read_yaml(path)
        if isinstance(data, dict):
            records.append(data)
    return records


def delete_record(
    area: str,
    record_id: str,
    repo_root: Path | None = None,
    layout: RuntimeLayout | None = None,
    mode: str | None = None,
) -> Path:
    path = record_path(area, record_id, repo_root, layout, mode)
    if not path.exists():
        raise FileNotFoundError(f"P6 record not found: {record_id}")
    path.unlink()
    return path


def redact_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: redact_secrets(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_secrets(v) for v in value]
    if not isinstance(value, str):
        return value
    redacted = re.sub(r"sk-[A-Za-z0-9]{12,}", "[REDACTED]", value)
    redacted = re.sub(r"Bearer\s+[A-Za-z0-9._-]+", "Bearer [REDACTED]", redacted)
    redacted = re.sub(r"api[_-]?key\s*[:=]\s*\S+", "api_key=[REDACTED]", redacted, flags=re.IGNORECASE)
    return redacted
