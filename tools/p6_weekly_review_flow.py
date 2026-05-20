#!/usr/bin/env python3
"""Run one real P6 weekly review flow from a provided Obsidian markdown note."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "apps" / "api" / "src"
if str(API_SRC) not in sys.path:
    sys.path.insert(0, str(API_SRC))

from alters_lab.schemas.action_alignment import (  # noqa: E402
    ActionAlignmentEvidence,
    ActionAlignmentScoreRequest,
    ActionAlignmentScores,
)
from alters_lab.schemas.weekly_review_session import WeeklyReviewCompleteRequest, WeeklyReviewStartRequest  # noqa: E402
from alters_lab.services.action_alignment import build_action_alignment_score, save_action_alignment_score  # noqa: E402
from alters_lab.services.obsidian_weekly_note import build_extracted_record, save_weekly_note_record  # noqa: E402
from alters_lab.services.weekly_review_session import (  # noqa: E402
    complete_weekly_review_session,
    save_weekly_review_session,
    start_weekly_review_session,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the P6 weekly review flow from a real markdown note.")
    parser.add_argument("weekly_note_path", type=Path)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--selected-alter-id", default=None)
    parser.add_argument("--review-note", required=True)
    parser.add_argument("--dialogue-summary", default="")
    parser.add_argument("--primary-next-correction", required=True)
    parser.add_argument("--supporting-action", action="append", default=[])
    parser.add_argument("--direction-alignment", type=float, required=True)
    parser.add_argument("--execution-consistency", type=float, required=True)
    parser.add_argument("--avoidance-level", type=float, required=True)
    parser.add_argument("--one-action-evidence", required=True)
    parser.add_argument("--one-avoidance-or-friction-evidence", required=True)
    parser.add_argument("--one-next-correction", required=True)
    parser.add_argument("--verdict-label", required=True)
    parser.add_argument("--verdict-sentence", required=True)
    return parser.parse_args(argv)


def run_weekly_review_flow(args: argparse.Namespace) -> dict[str, str]:
    repo_root = args.repo_root.resolve()
    note_path = args.weekly_note_path.resolve()
    raw_note = note_path.read_text(encoding="utf-8")

    note = build_extracted_record(raw_note, source_path=str(note_path))
    note_path_saved = save_weekly_note_record(note, repo_root)

    session = start_weekly_review_session(
        WeeklyReviewStartRequest(
            weekly_note_record_id=note.record_id,
            selected_alter_id=args.selected_alter_id,
            caller="p6_weekly_review_flow",
        ),
        repo_root=repo_root,
    )
    save_weekly_review_session(session, repo_root)

    completed = complete_weekly_review_session(
        session,
        WeeklyReviewCompleteRequest(
            review_note=args.review_note,
            dialogue_summary=args.dialogue_summary,
            primary_next_correction=args.primary_next_correction,
            supporting_actions=args.supporting_action[:2],
            caller="p6_weekly_review_flow",
        ),
    )
    session_path_saved = save_weekly_review_session(completed, repo_root)

    score = build_action_alignment_score(
        ActionAlignmentScoreRequest(
            session_id=completed.session_id,
            scores=ActionAlignmentScores(
                direction_alignment=args.direction_alignment,
                execution_consistency=args.execution_consistency,
                avoidance_level=args.avoidance_level,
            ),
            evidence=ActionAlignmentEvidence(
                one_action_evidence=args.one_action_evidence,
                one_avoidance_or_friction_evidence=args.one_avoidance_or_friction_evidence,
                one_next_correction=args.one_next_correction,
            ),
            verdict_label=args.verdict_label,
            verdict_sentence=args.verdict_sentence,
            caller="p6_weekly_review_flow",
        ),
        repo_root=repo_root,
    )
    score_path_saved = save_action_alignment_score(score, repo_root)

    return {
        "weekly_note_record_id": note.record_id,
        "weekly_note_path": str(note_path_saved),
        "weekly_review_session_id": completed.session_id,
        "weekly_review_path": str(session_path_saved),
        "calibration_record_id": score.score_id,
        "calibration_record_path": str(score_path_saved),
        "action_alignment_score": str(score.action_alignment_score),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_weekly_review_flow(args)
    for key, value in result.items():
        print(f"{key}={value}")
    print("provider_called=false")
    print("active_yaml_modified=false")
    print("rubric_modified=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
