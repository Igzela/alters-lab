#!/usr/bin/env python3
"""Guarded P6 behavior validation and closeout attempt."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "apps" / "api" / "src"
TOOLS_DIR = REPO_ROOT / "tools"
for path in (API_SRC, TOOLS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from alters_lab.schemas.behavior_validation import (  # noqa: E402
    BehaviorValidationEvaluateRequest,
    BehaviorValidationMetrics,
    UsageIntegrityAudit,
)
from alters_lab.services.behavior_validation import evaluate_behavior_validation, save_behavior_validation  # noqa: E402
from alters_lab.services.phase6_closeout import build_phase6_closeout_report  # noqa: E402
from p6_validation_check import collect_p6_evidence  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Attempt P6 behavior validation and closeout safely.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--dry-run", action="store_true", help="Do not save behavior validation records.")
    parser.add_argument(
        "--usage-integrity-pass",
        action="store_true",
        help="Operator attests usage integrity after reviewing evidence.",
    )
    parser.add_argument(
        "--behavior-improved",
        action="store_true",
        help="Operator attests behavior metrics improved after reviewing evidence.",
    )
    parser.add_argument(
        "--save-validation",
        action="store_true",
        help="Persist the behavior validation record when all gates pass.",
    )
    return parser.parse_args(argv)


def build_validation_request(summary) -> BehaviorValidationEvaluateRequest:
    return BehaviorValidationEvaluateRequest(
        weekly_review_ids=summary.weekly_review_ids,
        calibration_record_ids=summary.calibration_record_ids,
        pattern_review_ids=summary.pattern_review_ids,
        metrics=BehaviorValidationMetrics(
            action_alignment_score_improves=True,
            repeated_negative_patterns_reduce=True,
            primary_correction_completion_rate_improves=True,
        ),
        usage_integrity=UsageIntegrityAudit(
            weekly_notes_completed_honestly=True,
            calibration_records_created=True,
            primary_corrections_set=True,
            failure_reviews_honest=True,
            self_deception_risk_not_softened=True,
            sessions_not_skipped_too_often=True,
        ),
        save=False,
        caller="p6_closeout_attempt",
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    summary = collect_p6_evidence(repo_root)

    if not summary.validation_ready:
        print(f"BLOCKED: {summary.status}")
        for item in summary.missing_evidence:
            print(f"- {item}")
        print("phase6_closeout=BLOCKED")
        return 0

    if not args.usage_integrity_pass or not args.behavior_improved:
        print("BLOCKED: evidence is present, but operator validation flags are missing.")
        print("Required flags after manual evidence review: --usage-integrity-pass --behavior-improved")
        print("phase6_closeout=BLOCKED")
        return 0

    validation = evaluate_behavior_validation(build_validation_request(summary), repo_root=repo_root)
    print(f"behavior_validation_outcome={validation.outcome}")
    print(f"evidence_verified={str(validation.evidence_verified).lower()}")
    print(f"p6_sealed={str(validation.p6_sealed).lower()}")

    if args.dry_run:
        print("DRY_RUN: behavior validation was evaluated but not saved.")
        print("phase6_closeout=BLOCKED_UNTIL_VALIDATION_IS_PERSISTED")
        return 0

    if validation.outcome != "P6_BEHAVIOR_VALIDATED":
        print("BLOCKED: behavior validation did not pass.")
        print("phase6_closeout=BLOCKED")
        return 0

    if not args.save_validation:
        print("BLOCKED: validation passed in memory, but --save-validation was not supplied.")
        print("phase6_closeout=BLOCKED_UNTIL_VALIDATION_IS_PERSISTED")
        return 0

    path = save_behavior_validation(validation, repo_root=repo_root)
    print(f"behavior_validation_record_id={validation.validation_id}")
    print(f"behavior_validation_path={path}")

    closeout = build_phase6_closeout_report(repo_root)
    print(f"phase6_closeout={closeout.status}")
    print(f"sealed_baseline_candidate={str(closeout.summary.sealed_baseline_candidate).lower()}")
    for check in closeout.checks:
        print(f"{check.name}={check.status}: {check.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
