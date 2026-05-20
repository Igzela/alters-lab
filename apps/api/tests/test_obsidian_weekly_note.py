"""Tests for P6-M1 Obsidian weekly note ingest service."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from alters_lab.schemas.obsidian_weekly_note import WeeklyNoteEditPatch, WeeklyNoteIngestRequest
from alters_lab.services.obsidian_weekly_note import (
    apply_weekly_note_edit,
    build_extracted_record,
    list_weekly_note_records,
    load_weekly_note_record,
    parse_weekly_note_markdown,
    save_weekly_note_record,
)


VALID_NOTE = """# Weekly Review - 2026-05-20

## Session Type
personal

## Observable Facts
- Completed two focused coding sessions.
- Missed one planned review block.
- Slept before midnight on three nights.
- Deferred the provider integration decision.
- Wrote down the next correction.

## Subjective State
Tired but steady. Some anxiety around scope.

## Primary Problem
The week had too much parallel work.

## Friction / Avoidance
I avoided narrowing the work to one correction.

## Desired Correction
Pick one primary correction before starting new work.
"""


def test_parse_valid_semi_fixed_markdown():
    parsed = parse_weekly_note_markdown(VALID_NOTE)
    assert parsed.session_type_raw == "personal"
    assert len(parsed.observable_facts_raw) == 5
    assert "parallel work" in parsed.primary_problem_raw


def test_reject_missing_session_type():
    raw = VALID_NOTE.replace("## Session Type\npersonal\n", "")
    with pytest.raises(ValueError, match="Session Type"):
        build_extracted_record(raw)


def test_reject_invalid_session_type():
    raw = VALID_NOTE.replace("personal", "business", 1)
    with pytest.raises(ValueError, match="Invalid session_type"):
        build_extracted_record(raw)


def test_reject_fewer_than_five_observable_facts():
    raw = VALID_NOTE.replace("- Wrote down the next correction.\n", "")
    with pytest.raises(ValueError, match="at least 5"):
        build_extracted_record(raw)


def test_reject_more_than_seven_observable_facts():
    raw = VALID_NOTE.replace(
        "- Wrote down the next correction.\n",
        "- Wrote down the next correction.\n- Extra fact one.\n- Extra fact two.\n- Extra fact three.\n",
    )
    with pytest.raises(ValueError, match="at most 7"):
        build_extracted_record(raw)


def test_reject_subjective_state_longer_than_three_sentences():
    raw = VALID_NOTE.replace(
        "Tired but steady. Some anxiety around scope.",
        "One. Two. Three. Four.",
    )
    with pytest.raises(ValueError, match="at most 3"):
        build_extracted_record(raw)


def test_preserves_raw_note_and_marks_derived():
    record = build_extracted_record(VALID_NOTE, "weekly.md")
    assert record.raw_note == VALID_NOTE
    assert record.raw_note_preserved is True
    assert record.derived_from_raw_note is True
    assert record.source_path == "weekly.md"


def test_save_and_list_only_tmp_weekly_note_dir(tmp_path):
    record = build_extracted_record(VALID_NOTE)
    path = save_weekly_note_record(record, tmp_path)
    assert "alters/product/weekly_notes" in str(path)
    assert not (tmp_path / "alters" / "current").exists()
    records = list_weekly_note_records(tmp_path)
    assert [r.record_id for r in records] == [record.record_id]


def test_load_missing_record_raises_controlled_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_weekly_note_record("missing", tmp_path)


def test_edit_preserves_raw_note_and_produces_diff():
    record = build_extracted_record(VALID_NOTE)
    patch = WeeklyNoteEditPatch(
        observable_facts=[
            "Completed two focused coding sessions.",
            "Slept before midnight on three nights.",
            "Deferred the provider integration decision.",
            "Wrote down the next correction.",
            "Kept a single review note.",
        ],
        correction_note="Removed duplicate negative fact after checking source note.",
    )
    edited, diff = apply_weekly_note_edit(record, patch)
    assert edited.raw_note == record.raw_note
    assert diff.changed_fields == ["observable_facts"]
    assert "Missed one planned review block." in diff.deleted_negative_facts
    assert diff.challenge_required is True
    assert edited.edit_history[-1] == diff


def test_extra_fields_rejected():
    with pytest.raises(ValidationError):
        WeeklyNoteIngestRequest(raw_note=VALID_NOTE, provider={"name": "x"})  # type: ignore[call-arg]
