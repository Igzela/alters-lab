"""P6-M1 Obsidian weekly note ingest routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.obsidian_weekly_note import (
    WeeklyNoteEditPatch,
    WeeklyNoteEditResponse,
    WeeklyNoteHealthResponse,
    WeeklyNoteIngestRequest,
    WeeklyNoteIngestResponse,
    WeeklyNoteListResponse,
    WeeklyNoteLoadResponse,
)
from alters_lab.services.obsidian_weekly_note import (
    apply_weekly_note_edit,
    build_extracted_record,
    list_weekly_note_records,
    load_weekly_note_record,
    save_weekly_note_record,
)

router = APIRouter(prefix="/obsidian-weekly-note", tags=["obsidian-weekly-note"])


@router.get("/health", response_model=WeeklyNoteHealthResponse)
def health():
    return WeeklyNoteHealthResponse()


@router.post("/ingest", response_model=WeeklyNoteIngestResponse)
def ingest(body: WeeklyNoteIngestRequest):
    try:
        record = build_extracted_record(body.raw_note, body.source_path)
        path = save_weekly_note_record(record) if body.save else None
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return WeeklyNoteIngestResponse(
        status="saved" if body.save else "extracted",
        record=record,
        record_path=str(path) if path else None,
    )


@router.get("/list", response_model=WeeklyNoteListResponse)
def list_records():
    records = list_weekly_note_records()
    return WeeklyNoteListResponse(records=records, count=len(records))


@router.get("/{record_id}", response_model=WeeklyNoteLoadResponse)
def load(record_id: str):
    try:
        return WeeklyNoteLoadResponse(record=load_weekly_note_record(record_id))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Weekly note not found: {record_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{record_id}/edit", response_model=WeeklyNoteEditResponse)
def edit(record_id: str, body: WeeklyNoteEditPatch):
    try:
        record = load_weekly_note_record(record_id)
        updated, diff = apply_weekly_note_edit(record, body)
        path = save_weekly_note_record(updated)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Weekly note not found: {record_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return WeeklyNoteEditResponse(status="saved", record=updated, diff=diff, record_path=str(path))
