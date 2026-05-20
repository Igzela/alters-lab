from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
TOOLS_DIR = REPO_ROOT / "tools"


def _load_tool(name: str):
    path = TOOLS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


VALID_WEEKLY_NOTE = """# Weekly Review - 2026-05-20

## Session Type
project

## Observable Facts
- Shipped the P6 runtime code complete branch.
- Fixed the fake ID behavior validation blocker.
- Ran the backend test suite.
- Did not create behavior validation records.
- Did not mark P6 sealed.

## Subjective State
Focused but cautious.

## Primary Problem
P6 still needs real weekly evidence.

## Friction / Avoidance
The process can be mistaken for validation before evidence exists.

## Desired Correction
Run exactly one real weekly review per real week.
"""


def test_p6_validation_check_reports_empty_repo_blocked(tmp_path):
    validation_check = _load_tool("p6_validation_check")

    summary = validation_check.collect_p6_evidence(tmp_path)

    assert summary.status == "P6_BLOCKED_BY_REAL_USE_WINDOW"
    assert summary.weekly_review_count == 0
    assert summary.calibration_record_count == 0
    assert summary.pattern_review_count == 0
    assert not summary.evidence_verified


def test_p6_closeout_attempt_dry_run_blocks_empty_repo(tmp_path, capsys):
    closeout_attempt = _load_tool("p6_closeout_attempt")

    rc = closeout_attempt.main(["--repo-root", str(tmp_path), "--dry-run"])

    out = capsys.readouterr().out
    assert rc == 0
    assert "BLOCKED: P6_BLOCKED_BY_REAL_USE_WINDOW" in out
    assert "phase6_closeout=BLOCKED" in out


def test_p6_weekly_review_flow_writes_runtime_records_only_to_repo_root(tmp_path):
    weekly_flow = _load_tool("p6_weekly_review_flow")
    validation_check = _load_tool("p6_validation_check")
    note_path = tmp_path / "week1.md"
    note_path.write_text(VALID_WEEKLY_NOTE, encoding="utf-8")

    args = weekly_flow.parse_args(
        [
            str(note_path),
            "--repo-root",
            str(tmp_path),
            "--review-note",
            "Reviewed real Week 1 evidence and kept P6 unsealed.",
            "--primary-next-correction",
            "Run the next weekly review after one real week.",
            "--supporting-action",
            "Keep raw note content out of commits.",
            "--direction-alignment",
            "0.6",
            "--execution-consistency",
            "0.7",
            "--avoidance-level",
            "0.2",
            "--one-action-evidence",
            "Backend tests were run after the blocker fix.",
            "--one-avoidance-or-friction-evidence",
            "Validation could be confused with orchestration.",
            "--one-next-correction",
            "Wait for real Week 2 evidence.",
            "--verdict-label",
            "unstable_but_useful",
            "--verdict-sentence",
            "The process is useful but not yet validated.",
        ]
    )

    result = weekly_flow.run_weekly_review_flow(args)

    assert result["weekly_note_record_id"].startswith("weekly_note_")
    assert result["weekly_review_session_id"].startswith("weekly_review_")
    assert result["calibration_record_id"].startswith("action_alignment_")
    assert (tmp_path / "alters/product/weekly_notes").exists()
    assert (tmp_path / "alters/product/weekly_reviews").exists()
    assert (tmp_path / "alters/product/calibration_records").exists()
    assert not (tmp_path / "alters/current").exists()
    assert not (tmp_path / "alters/calibration/rubric.yaml").exists()

    summary = validation_check.collect_p6_evidence(tmp_path)
    assert summary.weekly_review_count == 1
    assert summary.calibration_record_count == 1
    assert summary.pattern_review_count == 0
    assert summary.status == "P6_BLOCKED_BY_REAL_USE_WINDOW"
