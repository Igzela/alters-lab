"""Tests for P4-M5 Rubric Delta Suggestion service."""

from __future__ import annotations

import pytest

from alters_lab.schemas.rubric_delta import RubricDeltaSuggestRequest, RubricDeltaSuggestion
from alters_lab.services.calibration_loop import RealityScoreRequest, submit_reality_score
from alters_lab.services.rubric_delta import (
    list_rubric_delta_suggestions,
    rubric_delta_boundary_confirmations,
    suggestion_directory,
    suggest_rubric_delta,
)


def _scores(value: int) -> dict:
    return {
        "execution_discipline": value,
        "exploration_freedom": value,
        "life_state_match": value,
        "energy_level": value,
    }


def _record(tmp_path, score_id: str, actual: int, expected: int | None = None):
    request = RealityScoreRequest(
        score_id=score_id,
        branch_id="branch_A",
        alter_id="alter_A",
        actual_scores=_scores(actual),
        expected_scores=_scores(expected) if expected is not None else None,
        submitted_by_user=True,
    )
    return submit_reality_score(request, tmp_path)


def test_insufficient_data_returns_insufficient_data(tmp_path):
    _record(tmp_path, "score_one", actual=3, expected=5)
    status, suggestion, path = suggest_rubric_delta(RubricDeltaSuggestRequest(min_records=2), tmp_path)
    assert status == "insufficient_data"
    assert suggestion is None
    assert path is None


def test_valid_repeated_mismatch_produces_pending_review_suggestion(tmp_path):
    _record(tmp_path, "score_one", actual=2, expected=5)
    _record(tmp_path, "score_two", actual=3, expected=5)
    status, suggestion, path = suggest_rubric_delta(RubricDeltaSuggestRequest(min_records=2), tmp_path)
    assert status == "suggested"
    assert path is None
    assert suggestion is not None
    assert suggestion.status == "pending_review"
    assert suggestion.source == "calibration_history"
    assert suggestion.rubric_write_allowed is False
    assert suggestion.human_confirmation_required is True
    assert {d.direction for d in suggestion.dimensions} == {"actual_lower_than_expected"}


def test_suggestion_never_allows_rubric_write():
    with pytest.raises(Exception):
        RubricDeltaSuggestion(
            id="rubric_delta_bad",
            status="pending_review",
            dimensions=[],
            summary="bad",
            evidence_refs=[],
            rubric_write_allowed=True,
            human_confirmation_required=True,
            created_at="2026-05-20T00:00:00+00:00",
            boundary_confirmations=rubric_delta_boundary_confirmations(),
        )


def test_save_suggestion_writes_only_tmp_suggestion_dir(tmp_path):
    _record(tmp_path, "score_one", actual=1, expected=5)
    _record(tmp_path, "score_two", actual=1, expected=5)
    rubric_path = tmp_path / "alters" / "calibration" / "rubric.yaml"
    rubric_path.parent.mkdir(parents=True, exist_ok=True)
    rubric_path.write_text("rubric: unchanged\n", encoding="utf-8")
    before = rubric_path.read_text(encoding="utf-8")

    status, suggestion, path = suggest_rubric_delta(
        RubricDeltaSuggestRequest(min_records=2, save_suggestion=True),
        tmp_path,
    )

    assert status == "saved"
    assert suggestion is not None
    assert path is not None
    assert path.parent == suggestion_directory(tmp_path)
    assert path.exists()
    assert rubric_path.read_text(encoding="utf-8") == before
    assert not (tmp_path / "alters" / "current").exists()


def test_extra_fields_auto_apply_write_rubric_rejected():
    with pytest.raises(Exception):
        RubricDeltaSuggestRequest(auto_apply=True)
    with pytest.raises(Exception):
        RubricDeltaSuggestRequest(write_rubric=True)


def test_list_suggestions_metadata_only(tmp_path):
    _record(tmp_path, "score_one", actual=1, expected=5)
    _record(tmp_path, "score_two", actual=1, expected=5)
    suggest_rubric_delta(RubricDeltaSuggestRequest(save_suggestion=True), tmp_path)
    suggestions = list_rubric_delta_suggestions(tmp_path)
    assert len(suggestions) == 1
    assert suggestions[0]["status"] == "pending_review"
    assert "dimensions" not in suggestions[0]
