#!/usr/bin/env python3
"""Inspect P6 real-use evidence without creating validation records."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "apps" / "api" / "src"
if str(API_SRC) not in sys.path:
    sys.path.insert(0, str(API_SRC))

from alters_lab.services.action_alignment import list_action_alignment_scores  # noqa: E402
from alters_lab.services.behavior_validation import verify_behavior_validation_evidence  # noqa: E402
from alters_lab.services.pattern_review import list_pattern_reviews  # noqa: E402
from alters_lab.services.weekly_review_session import list_weekly_review_sessions  # noqa: E402


@dataclass
class P6EvidenceSummary:
    status: str
    weekly_review_count: int
    calibration_record_count: int
    pattern_review_count: int
    weekly_review_ids: list[str]
    calibration_record_ids: list[str]
    pattern_review_ids: list[str]
    evidence_verified: bool
    evidence_window_days: int | None
    missing_evidence: list[str]

    @property
    def validation_ready(self) -> bool:
        return self.evidence_verified


def collect_p6_evidence(repo_root: Path) -> P6EvidenceSummary:
    weekly_reviews = [r for r in list_weekly_review_sessions(repo_root) if r.status == "completed"]
    weekly_reviews = sorted(weekly_reviews, key=lambda r: (r.created_at, r.session_id))
    weekly_review_ids = [r.session_id for r in weekly_reviews]
    weekly_review_id_set = set(weekly_review_ids)

    calibration_records = [
        record
        for record in list_action_alignment_scores(repo_root)
        if record.session_id in weekly_review_id_set
    ]
    calibration_records = sorted(calibration_records, key=lambda r: (r.created_at, r.score_id))
    calibration_record_ids = [r.score_id for r in calibration_records]

    pattern_reviews = [review for review in list_pattern_reviews(repo_root) if review.weeks_evaluated >= 4]
    pattern_reviews = sorted(pattern_reviews, key=lambda r: (r.created_at, r.review_id))
    pattern_review_ids = [r.review_id for r in pattern_reviews]

    missing: list[str] = []
    evidence_verified = False
    window_days: int | None = None
    try:
        evidence = verify_behavior_validation_evidence(
            weekly_ids=weekly_review_ids,
            calibration_ids=calibration_record_ids,
            pattern_ids=pattern_review_ids,
            repo_root=repo_root,
        )
        evidence_verified = bool(evidence["verified"])
        window_days = evidence["window_days"]
        missing.extend(evidence["errors"])
    except ValueError as exc:
        missing.append(str(exc))

    status = "P6_VALIDATION_READY"
    if not evidence_verified:
        if any("4-week validation window" in item for item in missing):
            status = "P6_BLOCKED_BY_TIME_WINDOW"
        else:
            status = "P6_BLOCKED_BY_REAL_USE_WINDOW"

    return P6EvidenceSummary(
        status=status,
        weekly_review_count=len(weekly_review_ids),
        calibration_record_count=len(calibration_record_ids),
        pattern_review_count=len(pattern_review_ids),
        weekly_review_ids=weekly_review_ids,
        calibration_record_ids=calibration_record_ids,
        pattern_review_ids=pattern_review_ids,
        evidence_verified=evidence_verified,
        evidence_window_days=window_days,
        missing_evidence=_unique(missing),
    )


def print_summary(summary: P6EvidenceSummary, json_output: bool) -> None:
    if json_output:
        print(json.dumps(asdict(summary), indent=2, sort_keys=True))
        return
    print(f"P6 validation evidence status: {summary.status}")
    print(f"weekly_review_count={summary.weekly_review_count}")
    print(f"calibration_record_count={summary.calibration_record_count}")
    print(f"pattern_review_count={summary.pattern_review_count}")
    print(f"evidence_verified={str(summary.evidence_verified).lower()}")
    print(f"evidence_window_days={summary.evidence_window_days}")
    if summary.missing_evidence:
        print("missing_evidence:")
        for item in summary.missing_evidence:
            print(f"- {item}")
    else:
        print("missing_evidence: none")


def _unique(items: list[str]) -> list[str]:
    seen = set()
    unique_items: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)
    return unique_items


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check P6 real-use validation evidence.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary = collect_p6_evidence(args.repo_root.resolve())
    print_summary(summary, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
