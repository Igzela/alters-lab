"""P4-M5 Rubric Delta Suggestion service.

Suggestions are derived from explicit calibration history only. This service
never writes the active rubric and never mutates active YAML.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

from alters_lab.schemas.calibration_loop import RealityScoreRecord
from alters_lab.schemas.rubric_delta import (
    RubricDeltaBoundaryConfirmations,
    RubricDeltaDimensionSuggestion,
    RubricDeltaSuggestRequest,
    RubricDeltaSuggestion,
)
from alters_lab.services.calibration_loop import DIMENSIONS, get_repo_root, list_reality_score_records


def rubric_delta_boundary_confirmations() -> dict:
    return RubricDeltaBoundaryConfirmations().model_dump()


def suggestion_directory(repo_root: Path | None = None) -> Path:
    root = repo_root or get_repo_root()
    return root / "alters" / "calibration" / "rubric_delta_suggestions"


def generate_suggestion_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"rubric_delta_{ts}_{uuid.uuid4().hex[:8]}"


def _record_has_expected_scores(record: RealityScoreRecord) -> bool:
    return record.expected_scores is not None


def _direction(lower_count: int, higher_count: int, mismatch_count: int) -> str:
    if lower_count > higher_count and lower_count > (mismatch_count / 2):
        return "actual_lower_than_expected"
    if higher_count > lower_count and higher_count > (mismatch_count / 2):
        return "actual_higher_than_expected"
    return "mixed"


def _severity(average_drift: float) -> str:
    if average_drift < 0.25:
        return "low"
    if average_drift < 0.6:
        return "medium"
    return "high"


def _suggestion_text(dimension: str, direction: str, average_drift: float) -> str:
    if direction == "actual_lower_than_expected":
        return (
            f"Review whether rubric expectations for {dimension} are too optimistic "
            f"or whether evidence collection misses constraints; average normalized drift is {average_drift:.2f}."
        )
    if direction == "actual_higher_than_expected":
        return (
            f"Review whether rubric expectations for {dimension} are too conservative "
            f"or whether current scoring underweights positive evidence; average normalized drift is {average_drift:.2f}."
        )
    return (
        f"Review {dimension} scoring examples for inconsistent interpretation; "
        f"average normalized drift is {average_drift:.2f} with mixed direction."
    )


def build_rubric_delta_suggestion(
    request: RubricDeltaSuggestRequest,
    repo_root: Path | None = None,
) -> tuple[str, RubricDeltaSuggestion | None]:
    records = [r for r in list_reality_score_records(repo_root) if _record_has_expected_scores(r)]
    if len(records) < request.min_records:
        return "insufficient_data", None

    dimensions: list[RubricDeltaDimensionSuggestion] = []
    evidence_refs: set[str] = set()

    for dimension in DIMENSIONS:
        drifts: list[float] = []
        lower_count = 0
        higher_count = 0
        mismatch_count = 0
        dimension_refs: list[str] = []

        for record in records:
            assert record.expected_scores is not None
            expected = getattr(record.expected_scores, dimension)
            actual = getattr(record.actual_scores, dimension)
            if expected == actual:
                continue
            mismatch_count += 1
            if actual < expected:
                lower_count += 1
            elif actual > expected:
                higher_count += 1
            drifts.append(abs(expected - actual) / 4)
            dimension_refs.append(record.id)

        if not drifts:
            continue

        average_drift = round(sum(drifts) / len(drifts), 4)
        if average_drift < request.drift_threshold:
            continue

        direction = _direction(lower_count, higher_count, mismatch_count)
        dimensions.append(RubricDeltaDimensionSuggestion(
            dimension=dimension,
            mismatch_count=mismatch_count,
            average_drift=average_drift,
            direction=direction,  # type: ignore[arg-type]
            suggestion=_suggestion_text(dimension, direction, average_drift),
            severity=_severity(average_drift),  # type: ignore[arg-type]
        ))
        evidence_refs.update(dimension_refs)

    if not dimensions:
        return "insufficient_data", None

    suggestion = RubricDeltaSuggestion(
        id=generate_suggestion_id(),
        dimensions=dimensions,
        summary=(
            f"Detected repeated calibration mismatch in {len(dimensions)} dimension(s). "
            "This is a pending review suggestion only and does not modify rubric.yaml."
        ),
        evidence_refs=sorted(evidence_refs),
        created_at=datetime.now(timezone.utc).isoformat(),
        boundary_confirmations=RubricDeltaBoundaryConfirmations(),
    )
    return "suggested", suggestion


def save_rubric_delta_suggestion(
    suggestion: RubricDeltaSuggestion,
    repo_root: Path | None = None,
) -> Path:
    directory = suggestion_directory(repo_root)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{suggestion.id}.yaml"
    path.write_text(
        yaml.safe_dump(suggestion.model_dump(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


def suggest_rubric_delta(
    request: RubricDeltaSuggestRequest,
    repo_root: Path | None = None,
) -> tuple[str, RubricDeltaSuggestion | None, Path | None]:
    status, suggestion = build_rubric_delta_suggestion(request, repo_root)
    if suggestion is None:
        return status, None, None
    if request.save_suggestion:
        path = save_rubric_delta_suggestion(suggestion, repo_root)
        return "saved", suggestion, path
    return status, suggestion, None


def list_rubric_delta_suggestions(repo_root: Path | None = None) -> list[dict]:
    directory = suggestion_directory(repo_root)
    if not directory.exists():
        return []

    suggestions: list[dict] = []
    for path in sorted(directory.glob("rubric_delta_*.yaml")):
        if path.name == "_template.yaml":
            continue
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            continue
        suggestions.append({
            "id": raw.get("id", path.stem),
            "status": raw.get("status"),
            "created_at": raw.get("created_at"),
            "dimension_count": len(raw.get("dimensions", [])) if isinstance(raw.get("dimensions"), list) else 0,
            "path": str(path),
        })
    return suggestions
