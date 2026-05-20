"""P6-M7 four-week pattern review service."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.pattern_review import (
    PatternReviewRecord,
    PatternReviewRequest,
    TriggeredPattern,
)
from alters_lab.services.p6_runtime import generate_record_id, list_records, read_record, utc_now, write_record


def build_pattern_review(request: PatternReviewRequest) -> PatternReviewRecord:
    last_four = request.weekly_patterns[-4:]
    if len(last_four) < 4:
        return PatternReviewRecord(
            review_id=generate_record_id("pattern_review"),
            status="insufficient_data",
            weeks_evaluated=len(last_four),
            created_at=utc_now(),
        )
    counts: dict[str, list[float]] = {}
    for signal in last_four:
        for pattern in signal.patterns:
            if signal.confidence >= 0.8:
                counts.setdefault(pattern, []).append(signal.confidence)
    triggered = [
        TriggeredPattern(
            pattern=pattern,  # type: ignore[arg-type]
            occurrences=len(confidences),
            confidence=round(sum(confidences) / len(confidences), 4),
            strategy_constraint=f"Next week primary correction must directly reduce {pattern}.",
        )
        for pattern, confidences in counts.items()
        if len(confidences) >= 3
    ]
    return PatternReviewRecord(
        review_id=generate_record_id("pattern_review"),
        status="pattern_triggered" if triggered else "no_pattern",
        weeks_evaluated=4,
        triggered_patterns=triggered,
        created_at=utc_now(),
    )


def save_pattern_review(record: PatternReviewRecord, repo_root: Path | None = None) -> Path:
    return write_record("pattern_reviews", record.review_id, record.model_dump(), repo_root)


def load_pattern_review(review_id: str, repo_root: Path | None = None) -> PatternReviewRecord:
    return PatternReviewRecord(**read_record("pattern_reviews", review_id, repo_root))


def list_pattern_reviews(repo_root: Path | None = None) -> list[PatternReviewRecord]:
    return [PatternReviewRecord(**r) for r in list_records("pattern_reviews", repo_root)]
