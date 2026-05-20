"""P6-M1 Obsidian weekly note ingest service."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from alters_lab.schemas.obsidian_weekly_note import (
    SessionType,
    WeeklyNoteEditDiff,
    WeeklyNoteEditPatch,
    WeeklyNoteExtractedRecord,
    WeeklyNoteSectionParse,
)
from alters_lab.services.p6_runtime import (
    generate_record_id,
    list_records,
    read_record,
    runtime_dir,
    utc_now,
    write_record,
)

ALLOWED_SESSION_TYPES = {"personal", "project", "learning", "relationship"}
NEGATIVE_FACT_PATTERNS = (
    "avoid",
    "avoided",
    "blocked",
    "failed",
    "friction",
    "missed",
    "not ",
    "stuck",
    "delayed",
    "late",
    "回避",
    "失败",
    "没",
    "不能",
    "卡住",
    "拖延",
)


def validate_session_type(value: str) -> SessionType:
    normalized = value.strip().lower()
    if normalized not in ALLOWED_SESSION_TYPES:
        raise ValueError(f"Invalid session_type: {value}")
    return normalized  # type: ignore[return-value]


def _sentence_count(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    parts = [p for p in re.split(r"[.!?。！？]+", stripped) if p.strip()]
    return max(1, len(parts))


def validate_subjective_state(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        raise ValueError("subjective_state must not be blank")
    if _sentence_count(stripped) > 3:
        raise ValueError("subjective_state must be at most 3 sentences")
    return stripped


def validate_observable_facts(facts: list[str]) -> list[str]:
    normalized = [f.strip() for f in facts if f.strip()]
    if len(normalized) < 5:
        raise ValueError("observable_facts must include at least 5 items")
    if len(normalized) > 7:
        raise ValueError("observable_facts must include at most 7 items")
    return normalized


def parse_weekly_note_markdown(raw_note: str) -> WeeklyNoteSectionParse:
    sections: dict[str, list[str]] = {}
    current_key: str | None = None

    for line in raw_note.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current_key = _normalize_heading(heading.group(1))
            sections[current_key] = []
            continue
        if current_key:
            sections[current_key].append(line)

    required = {
        "session_type": "Session Type",
        "observable_facts": "Observable Facts",
        "subjective_state": "Subjective State",
        "primary_problem": "Primary Problem",
        "friction_avoidance": "Friction / Avoidance",
        "desired_correction": "Desired Correction",
    }
    missing = [label for key, label in required.items() if key not in sections]
    if missing:
        raise ValueError(f"Missing weekly note section(s): {', '.join(missing)}")

    warnings: list[str] = []
    facts = extract_observable_facts(sections["observable_facts"])
    for fact in facts:
        if _looks_interpretive(fact):
            warnings.append(f"Observable fact may contain interpretation: {fact}")

    return WeeklyNoteSectionParse(
        session_type_raw=_section_text(sections["session_type"]),
        observable_facts_raw=facts,
        subjective_state_raw=_section_text(sections["subjective_state"]),
        primary_problem_raw=_section_text(sections["primary_problem"]),
        friction_or_avoidance_point_raw=_section_text(sections["friction_avoidance"]),
        desired_correction_raw=_section_text(sections["desired_correction"]),
        warnings=warnings,
    )


def extract_observable_facts(lines: list[str]) -> list[str]:
    facts: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("-"):
            fact = stripped[1:].strip()
            if fact:
                facts.append(fact)
        else:
            facts.append(stripped)
    return facts


def build_extracted_record(raw_note: str, source_path: str | None = None) -> WeeklyNoteExtractedRecord:
    parsed = parse_weekly_note_markdown(raw_note)
    session_type = validate_session_type(parsed.session_type_raw)
    facts = validate_observable_facts(parsed.observable_facts_raw)
    subjective_state = validate_subjective_state(parsed.subjective_state_raw)
    now = utc_now()
    return WeeklyNoteExtractedRecord(
        record_id=generate_weekly_note_record_id(now[:10]),
        source_path=source_path,
        raw_note=raw_note,
        session_type=session_type,
        observable_facts=facts,
        subjective_state=subjective_state,
        primary_problem=parsed.primary_problem_raw.strip(),
        friction_or_avoidance_point=parsed.friction_or_avoidance_point_raw.strip(),
        desired_correction=parsed.desired_correction_raw.strip(),
        extraction_warnings=parsed.warnings,
        created_at=now,
    )


def generate_weekly_note_record_id(date: str) -> str:
    compact_date = re.sub(r"[^0-9]", "", date) or "undated"
    return generate_record_id(f"weekly_note_{compact_date}")


def get_weekly_note_dir(repo_root: Path | None = None) -> Path:
    return runtime_dir("weekly_notes", repo_root)


def save_weekly_note_record(record: WeeklyNoteExtractedRecord, repo_root: Path | None = None) -> Path:
    return write_record("weekly_notes", record.record_id, record.model_dump(), repo_root)


def load_weekly_note_record(record_id: str, repo_root: Path | None = None) -> WeeklyNoteExtractedRecord:
    return WeeklyNoteExtractedRecord(**read_record("weekly_notes", record_id, repo_root))


def list_weekly_note_records(repo_root: Path | None = None) -> list[WeeklyNoteExtractedRecord]:
    return [WeeklyNoteExtractedRecord(**r) for r in list_records("weekly_notes", repo_root)]


def apply_weekly_note_edit(record: WeeklyNoteExtractedRecord, patch: WeeklyNoteEditPatch) -> tuple[WeeklyNoteExtractedRecord, WeeklyNoteEditDiff]:
    before = record.model_dump()
    updated = record.model_copy(deep=True)
    for field in (
        "session_type",
        "observable_facts",
        "subjective_state",
        "primary_problem",
        "friction_or_avoidance_point",
        "desired_correction",
    ):
        value = getattr(patch, field)
        if value is not None:
            setattr(updated, field, value)

    updated.observable_facts = validate_observable_facts(updated.observable_facts)
    updated.subjective_state = validate_subjective_state(updated.subjective_state)
    updated.updated_at = utc_now()

    diff = build_edit_diff(before, updated.model_dump(), patch.correction_note)
    updated.edit_history.append(diff)
    return updated, diff


def build_edit_diff(before: dict[str, Any], after: dict[str, Any], correction_note: str) -> WeeklyNoteEditDiff:
    fields = [
        "session_type",
        "observable_facts",
        "subjective_state",
        "primary_problem",
        "friction_or_avoidance_point",
        "desired_correction",
    ]
    changed = [field for field in fields if before.get(field) != after.get(field)]
    before_facts = set(before.get("observable_facts", []))
    after_facts = set(after.get("observable_facts", []))
    deleted = sorted(before_facts - after_facts)
    deleted_negative = [fact for fact in deleted if _is_negative_fact(fact)]
    challenge = bool(deleted_negative)
    return WeeklyNoteEditDiff(
        changed_fields=changed,
        deleted_facts=deleted,
        deleted_negative_facts=deleted_negative,
        challenge_required=challenge,
        challenge_question="这是事实修正，还是叙事软化？" if challenge else None,
        correction_note=correction_note,
        edited_at=utc_now(),
    )


def should_challenge_edit(diff: WeeklyNoteEditDiff) -> bool:
    return diff.challenge_required


def _normalize_heading(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.strip().lower())
    aliases = {
        "session type": "session_type",
        "observable facts": "observable_facts",
        "subjective state": "subjective_state",
        "primary problem": "primary_problem",
        "friction / avoidance": "friction_avoidance",
        "friction/avoidance": "friction_avoidance",
        "desired correction": "desired_correction",
    }
    return aliases.get(normalized, normalized.replace(" ", "_"))


def _section_text(lines: list[str]) -> str:
    return "\n".join(line.strip() for line in lines if line.strip()).strip()


def _looks_interpretive(fact: str) -> bool:
    return any(word in fact.lower() for word in ("probably", "should", "seems", "because", "felt like"))


def _is_negative_fact(fact: str) -> bool:
    lower = fact.lower()
    return any(pattern in lower for pattern in NEGATIVE_FACT_PATTERNS)
