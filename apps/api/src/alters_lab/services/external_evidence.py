"""External evidence service — save/load observed real-world outcomes."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.external_evidence import ExternalEvidenceRecord
from alters_lab.services.p6_runtime import (
    list_records,
    read_record,
    write_record,
)

AREA = "external_evidence"


def save_evidence(record: ExternalEvidenceRecord, repo_root: Path | None = None) -> Path:
    data = record.model_dump(mode="json")
    return write_record(AREA, record.evidence_id, data, repo_root=repo_root)


def load_evidence(evidence_id: str, repo_root: Path | None = None) -> ExternalEvidenceRecord:
    data = read_record(AREA, evidence_id, repo_root=repo_root)
    return ExternalEvidenceRecord(**data)


def list_evidence(repo_root: Path | None = None) -> list[ExternalEvidenceRecord]:
    records = list_records(AREA, repo_root=repo_root)
    return [ExternalEvidenceRecord(**r) for r in records]


def list_evidence_for_branch(branch_id: str, repo_root: Path | None = None) -> list[ExternalEvidenceRecord]:
    return [e for e in list_evidence(repo_root=repo_root) if e.branch_id == branch_id]


def list_evidence_for_snapshot(snapshot_id: str, repo_root: Path | None = None) -> list[ExternalEvidenceRecord]:
    return [e for e in list_evidence(repo_root=repo_root) if e.snapshot_id == snapshot_id]
