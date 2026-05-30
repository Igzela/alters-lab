"""P4 calibration loop MVP service.

Reality scores are explicit user submissions. Drift is computed as response-only
evidence and does not trigger regeneration, archive, promotion, or rubric writes.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from alters_lab.services import io
from alters_lab.schemas.calibration_loop import (
    CalibrationInputRefs,
    CalibrationLoopBoundaryConfirmations,
    CalibrationScoreValues,
    DriftCalculationRequest,
    DriftCalculationResult,
    RealityScoreRecord,
    RealityScoreRequest,
)

DIMENSIONS = (
    "execution_discipline",
    "exploration_freedom",
    "life_state_match",
    "energy_level",
)


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def calibration_boundary_confirmations() -> CalibrationLoopBoundaryConfirmations:
    return CalibrationLoopBoundaryConfirmations()


def score_directory(repo_root: Path | None = None) -> Path:
    root = repo_root or get_repo_root()
    return root / "alters" / "calibration" / "scores"


def generate_score_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"score_{ts}_{uuid.uuid4().hex[:8]}"


def _score_path(score_id: str, repo_root: Path | None = None) -> Path:
    return score_directory(repo_root) / f"{score_id}.yaml"


def _scores_to_plain_dict(scores: CalibrationScoreValues) -> dict[str, int]:
    return {dimension: getattr(scores, dimension) for dimension in DIMENSIONS}


def build_reality_score_record(
    request: RealityScoreRequest,
    created_at: str | None = None,
) -> RealityScoreRecord:
    score_id = request.score_id or generate_score_id()
    return RealityScoreRecord(
        id=score_id,
        created_at=created_at or datetime.now(timezone.utc).isoformat(),
        branch_id=request.branch_id,
        alter_id=request.alter_id,
        input_refs=CalibrationInputRefs(alter_ref=f"alters/current/alters/{request.alter_id}.yaml"),
        actual_scores=request.actual_scores,
        expected_scores=request.expected_scores,
        drift=None,
        user_notes=request.user_notes,
        evidence_refs=list(request.evidence_refs),
        submitted_by_user=True,
        source="explicit_user_submission",
        caller=request.caller,
        boundary_confirmations=calibration_boundary_confirmations(),
    )


def record_to_yaml_dict(record: RealityScoreRecord) -> dict:
    data = record.model_dump()
    data["quality_rules"] = [
        "Actual values must come from explicit user submission.",
        "No score values may be inferred from provider output.",
        "Drift evidence must not trigger automatic regeneration.",
        "Rubric changes require explicit human decision.",
    ]
    return data


def load_reality_score_record(path: Path) -> RealityScoreRecord:
    raw = io.read_yaml(path)
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid reality score record: {path}")
    raw.pop("quality_rules", None)
    return RealityScoreRecord(**raw)


def _idempotency_fields(record: RealityScoreRecord) -> dict:
    data = record.model_dump()
    data.pop("created_at", None)
    data.pop("boundary_confirmations", None)
    return data


def submit_reality_score(
    request: RealityScoreRequest,
    repo_root: Path | None = None,
) -> tuple[str, RealityScoreRecord, Path]:
    record = build_reality_score_record(request)
    path = _score_path(record.id, repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        existing = load_reality_score_record(path)
        if _idempotency_fields(existing) == _idempotency_fields(record):
            return "already_exists", existing, path
        raise ValueError(f"Reality score already exists with different content: {record.id}")

    io.write_yaml(path, record_to_yaml_dict(record), sort_keys=False, allow_unicode=True)
    return "recorded", record, path


def calculate_drift_values(
    expected_scores: CalibrationScoreValues,
    actual_scores: CalibrationScoreValues,
    threshold: float = 0.6,
) -> dict:
    per_dimension = {}
    for dimension in DIMENSIONS:
        expected = getattr(expected_scores, dimension)
        actual = getattr(actual_scores, dimension)
        per_dimension[dimension] = round(abs(expected - actual) / 4, 4)
    overall = round(sum(per_dimension.values()) / len(DIMENSIONS), 4)
    return {
        "per_dimension": per_dimension,
        "overall": overall,
        "checkpoint_threshold": threshold,
        "threshold_exceeded": overall >= threshold,
    }


def calculate_drift(request: DriftCalculationRequest) -> DriftCalculationResult:
    result = calculate_drift_values(request.expected_scores, request.actual_scores)
    return DriftCalculationResult(
        branch_id=request.branch_id,
        alter_id=request.alter_id,
        score_id=request.score_id,
        per_dimension=result["per_dimension"],
        overall=result["overall"],
        checkpoint_threshold=result["checkpoint_threshold"],
        threshold_exceeded=result["threshold_exceeded"],
        evidence_only=True,
        regeneration_triggered=False,
        rubric_modified=False,
        boundary_confirmations=calibration_boundary_confirmations(),
    )


def list_reality_score_records(repo_root: Path | None = None) -> list[RealityScoreRecord]:
    directory = score_directory(repo_root)
    if not directory.exists():
        return []

    records: list[RealityScoreRecord] = []
    for path in sorted(directory.glob("score_*.yaml")):
        if path.name == "_template.yaml":
            continue
        records.append(load_reality_score_record(path))
    return records


def build_calibration_history(repo_root: Path | None = None) -> dict:
    records = list_reality_score_records(repo_root)
    drift_evidence: list[DriftCalculationResult] = []
    for record in records:
        if record.expected_scores is None:
            continue
        drift_evidence.append(calculate_drift(DriftCalculationRequest(
            actual_scores=record.actual_scores,
            expected_scores=record.expected_scores,
            branch_id=record.branch_id,
            alter_id=record.alter_id,
            score_id=record.id,
        )))
    return {
        "records": records,
        "drift_evidence": drift_evidence,
        "count": len(records),
        "boundary_confirmations": calibration_boundary_confirmations(),
    }
