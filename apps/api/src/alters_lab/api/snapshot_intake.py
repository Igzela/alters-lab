from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.snapshot import (
    AnchorAnswerRequest,
    AnchorName,
    NextAnchorResponse,
    SnapshotConfirmationResponse,
    SnapshotPersistRequest,
    SnapshotPersistResponse,
    SnapshotSessionRead,
)
from pathlib import Path

from alters_lab.services.snapshot_intake import (
    create_empty_snapshot,
    mark_snapshot_completed,
    next_anchor,
    ready_for_confirmation,
    record_anchor_answer,
)
from alters_lab.services.snapshot_persist import (
    build_snapshot_persist_payload,
    persist_snapshot_to_disk,
    sha256_file,
    validate_snapshot_persist_governance,
)
from alters_lab.services.snapshot_sessions import InMemorySnapshotSessionStore

router = APIRouter(prefix="/snapshot-intake", tags=["snapshot-intake"])

store = InMemorySnapshotSessionStore()


def _session_to_read(session) -> SnapshotSessionRead:
    return SnapshotSessionRead(
        session_id=session.session_id,
        snapshot=session.snapshot,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("/health")
def health():
    return {"status": "ok", "component": "snapshot-intake"}


@router.post("/sessions", response_model=SnapshotSessionRead, status_code=201)
def create_session():
    snapshot = create_empty_snapshot()
    session = store.create_session(snapshot)
    return _session_to_read(session)


@router.get("/sessions/{session_id}", response_model=SnapshotSessionRead)
def get_session(session_id: UUID):
    session = store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    return _session_to_read(session)


@router.get("/sessions/{session_id}/next-anchor", response_model=NextAnchorResponse)
def get_next_anchor(session_id: UUID):
    session = store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    anchor = next_anchor(session.snapshot)
    return NextAnchorResponse(
        session_id=session.session_id,
        next_anchor=anchor,
        phase=session.snapshot.intake_status.phase,
    )


@router.post("/sessions/{session_id}/answers", response_model=SnapshotSessionRead)
def submit_answer(session_id: UUID, body: AnchorAnswerRequest):
    session = store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")

    current_pending = session.snapshot.intake_status.pending_anchor

    if body.anchor not in [a for a in AnchorName]:
        raise HTTPException(status_code=422, detail="unknown anchor name")

    if current_pending is None:
        raise HTTPException(status_code=409, detail="all anchors already answered")

    if body.anchor != current_pending:
        raise HTTPException(
            status_code=409,
            detail=f"expected anchor {current_pending.value}, got {body.anchor.value}",
        )

    completed = session.snapshot.intake_status.completed_anchors
    if body.anchor in completed:
        raise HTTPException(status_code=409, detail=f"anchor {body.anchor.value} already answered")

    try:
        updated_snapshot = record_anchor_answer(session.snapshot, body.anchor, body.answer)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    session.snapshot = updated_snapshot
    store.update_session(session)
    return _session_to_read(session)


@router.post(
    "/sessions/{session_id}/confirm",
    response_model=SnapshotConfirmationResponse,
)
def confirm_snapshot(session_id: UUID):
    session = store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")

    if not ready_for_confirmation(session.snapshot):
        raise HTTPException(
            status_code=409,
            detail="not ready for confirmation: all three anchors must be answered first",
        )

    completed_snapshot = mark_snapshot_completed(session.snapshot)
    session.snapshot = completed_snapshot
    store.update_session(session)

    return SnapshotConfirmationResponse(
        session_id=session.session_id,
        snapshot=completed_snapshot,
        ready_for_branch_discovery=True,
    )


@router.post(
    "/sessions/{session_id}/persist",
    response_model=SnapshotPersistResponse,
)
def persist_snapshot(session_id: UUID, body: SnapshotPersistRequest):
    session = store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")

    governance = validate_snapshot_persist_governance(session.snapshot)
    if not governance["valid"]:
        raise HTTPException(
            status_code=403,
            detail=f"governance validation failed: {'; '.join(governance['errors'])}",
        )

    if not body.approval_token:
        raise HTTPException(status_code=403, detail="approval_token is required")

    payload = build_snapshot_persist_payload(session.snapshot)
    target = Path("alters/current/snapshot.yaml")
    result = persist_snapshot_to_disk(
        payload,
        target,
        body.approval_token,
        dry_run=body.dry_run,
    )

    if result["status"] == "rejected":
        raise HTTPException(status_code=403, detail=result["reason"])

    yaml_before = sha256_file(target)

    return SnapshotPersistResponse(
        status=result["status"],
        path=result["path"],
        sha256_before=result["sha256_before"],
        sha256_after=result["sha256_after"],
        audit_record=result.get("audit_record", {}),
        governance_check=governance,
        boundary_confirmations={
            "read_only": False,
            "snapshot_yaml_modified": result["status"] == "persisted",
            "other_yaml_not_modified": True,
            "approval_token_hash_only": True,
        },
        would_write=result.get("would_write"),
    )
