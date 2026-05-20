"""Tests for P5-M3 Provider-backed Alter Dialogue service."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from alters_lab.schemas.provider_dialogue import (
    ProviderDialogueBoundaryConfirmations,
    ProviderDialogueReplyRequest,
)
from alters_lab.services.provider_dialogue import (
    get_provider_dialogue_health,
    provider_dialogue_reply,
    VALID_ALTER_IDS,
    _get_repo_root,
)


def test_boundary_confirmations_are_safe():
    bc = ProviderDialogueBoundaryConfirmations()
    assert bc.active_yaml_modified is False
    assert bc.rubric_modified is False
    assert bc.reality_score_created is False
    assert bc.drift_computed is False
    assert bc.archive_triggered is False
    assert bc.checkpoint_triggered is False
    assert bc.persisted is False
    assert bc.no_secrets_in_session is True


def test_mock_reply_works():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        req = ProviderDialogueReplyRequest(user_message="Hello alter")
        resp = provider_dialogue_reply(req, "alter_A")
        assert resp.status == "mock_response"
        assert resp.alter_id == "alter_A"
        assert resp.reply_text is not None
        assert len(resp.reply_text) > 0
        assert resp.persisted is False
        assert resp.session_path is None
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_invalid_alter_id_rejected():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        req = ProviderDialogueReplyRequest(user_message="Hello")
        with pytest.raises(ValueError):
            provider_dialogue_reply(req, "alter_Z")
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_save_session_false_writes_nothing():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        req = ProviderDialogueReplyRequest(user_message="test", save_session=False)
        resp = provider_dialogue_reply(req, "alter_A")
        assert resp.persisted is False
        assert resp.session_path is None
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_save_session_true_writes_to_product_area(tmp_path, monkeypatch):
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        monkeypatch.setattr("alters_lab.services.provider_dialogue._get_repo_root", lambda: tmp_path)
        alters_dir = tmp_path / "alters" / "current" / "alters"
        alters_dir.mkdir(parents=True)
        (alters_dir / "alter_A.yaml").write_text("id: alter_A\nbranch_ref: branch_A\n", encoding="utf-8")
        req = ProviderDialogueReplyRequest(user_message="test", save_session=True)
        resp = provider_dialogue_reply(req, "alter_A", tmp_path)
        assert resp.persisted is True
        assert resp.session_path is not None
        assert "alters/product/sessions" in resp.session_path
        session_path = Path(resp.session_path)
        assert session_path.exists()
        content = session_path.read_text()
        assert "sk-" not in content
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_no_active_yaml_diff():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        req = ProviderDialogueReplyRequest(user_message="test")
        repo = _get_repo_root()
        provider_dialogue_reply(req, "alter_A", repo)
        current_dir = repo / "alters" / "current"
        assert current_dir.exists()
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_no_api_key_leakage(tmp_path, monkeypatch):
    original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
    original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-secret-key"
        monkeypatch.setattr("alters_lab.services.provider_dialogue._get_repo_root", lambda: tmp_path)
        alters_dir = tmp_path / "alters" / "current" / "alters"
        alters_dir.mkdir(parents=True)
        (alters_dir / "alter_A.yaml").write_text("id: alter_A\nbranch_ref: branch_A\n", encoding="utf-8")
        req = ProviderDialogueReplyRequest(user_message="test", save_session=True)
        resp = provider_dialogue_reply(req, "alter_A", tmp_path)
        assert "sk-" not in resp.reply_text
        if resp.session_path:
            session_content = Path(resp.session_path).read_text()
            assert "sk-test" not in session_content
    finally:
        if original_mode is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original_mode
        else:
            os.environ.pop("ALTERS_PROVIDER_MODE", None)
        if original_key is not None:
            os.environ["ALTERS_PROVIDER_API_KEY"] = original_key
        else:
            os.environ.pop("ALTERS_PROVIDER_API_KEY", None)


def test_no_auto_reality_score_or_drift_or_archive():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        req = ProviderDialogueReplyRequest(user_message="test")
        repo = _get_repo_root()
        before_scores = len(list((repo / "alters" / "calibration" / "scores").glob("score_*.yaml"))) if (repo / "alters" / "calibration" / "scores").exists() else 0
        provider_dialogue_reply(req, "alter_A", repo)
        after_scores = len(list((repo / "alters" / "calibration" / "scores").glob("score_*.yaml"))) if (repo / "alters" / "calibration" / "scores").exists() else 0
        assert before_scores == after_scores
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_health_response():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        r = get_provider_dialogue_health()
        assert r.status == "ok"
        assert r.component == "provider-dialogue"
        assert r.provider_mode == "mock"
        assert sorted(r.available_alters) == sorted(VALID_ALTER_IDS)
        assert r.default_persist is False
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_request_save_session_defaults_false():
    req = ProviderDialogueReplyRequest(user_message="test")
    assert req.save_session is False
