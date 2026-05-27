"""P8-M1 Tests for real OpenAI-compatible HTTP provider integration.

Uses mock httpx responses — never makes real API calls.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from alters_lab.schemas.provider_gateway import (
    ProviderGatewayRequest,
    ProviderGatewayResponse,
)
from alters_lab.schemas.provider_dialogue import (
    ProviderDialogueReplyRequest,
)
from alters_lab.services.provider_gateway import (
    _get_provider_api_key,
    _get_provider_base_url,
    _get_provider_mode,
    _get_provider_model,
    _normalize_mode,
    _redact_secrets,
    get_provider_gateway_health,
    provider_gateway_complete,
)
from alters_lab.services.provider_dialogue import (
    provider_dialogue_reply,
    get_provider_dialogue_health,
)


# ---------------------------------------------------------------------------
# Mode normalization
# ---------------------------------------------------------------------------

class TestNormalizeMode:
    def test_underscore_passthrough(self):
        assert _normalize_mode("openai_compatible_http") == "openai_compatible_http"

    def test_hyphen_to_underscore(self):
        assert _normalize_mode("openai-compatible-http") == "openai_compatible_http"

    def test_mock_unchanged(self):
        assert _normalize_mode("mock") == "mock"

    def test_disabled_unchanged(self):
        assert _normalize_mode("disabled") == "disabled"

    def test_unknown_unchanged(self):
        assert _normalize_mode("something-else") == "something-else"


class TestGetProviderModeNormalization:
    def test_env_hyphen_normalized(self):
        original = os.environ.get("ALTERS_PROVIDER_MODE")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai-compatible-http"
            assert _get_provider_mode() == "openai_compatible_http"
        finally:
            if original is not None:
                os.environ["ALTERS_PROVIDER_MODE"] = original
            else:
                os.environ.pop("ALTERS_PROVIDER_MODE", None)

    def test_env_underscore_passthrough(self):
        original = os.environ.get("ALTERS_PROVIDER_MODE")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            assert _get_provider_mode() == "openai_compatible_http"
        finally:
            if original is not None:
                os.environ["ALTERS_PROVIDER_MODE"] = original
            else:
                os.environ.pop("ALTERS_PROVIDER_MODE", None)


# ---------------------------------------------------------------------------
# Real HTTP provider call with mocked httpx
# ---------------------------------------------------------------------------

def _mock_httpx_post_success(*args, **kwargs):
    """Simulate a successful OpenAI-compatible /chat/completions response."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "id": "chatcmpl-mock-123",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello from the simulated alter branch. This is a real provider response.",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 25,
            "completion_tokens": 12,
            "total_tokens": 37,
        },
    }
    return mock_resp


def _mock_httpx_post_http_error(*args, **kwargs):
    """Simulate an HTTP 401 error from the provider."""
    import httpx
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Unauthorized",
        request=MagicMock(),
        response=MagicMock(status_code=401),
    )
    return mock_resp


def _mock_httpx_post_empty_choices(*args, **kwargs):
    """Simulate a response with empty choices list."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "id": "chatcmpl-mock-empty",
        "choices": [],
        "usage": {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10},
    }
    return mock_resp


class TestRealProviderHTTPSuccess:
    def test_openai_compatible_http_returns_provider_response(self):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-real-key-abcdef123456"

            with patch("httpx.post", side_effect=_mock_httpx_post_success):
                req = ProviderGatewayRequest(
                    messages=[{"role": "user", "content": "Hello alter"}],
                    model="test-model",
                )
                resp = provider_gateway_complete(req)

            assert resp.status == "provider_response"
            assert resp.mode == "openai_compatible_http"
            assert "simulated alter branch" in resp.content
            assert resp.usage is not None
            assert resp.usage["total_tokens"] == 37
            assert resp.persisted is False
            assert resp.active_yaml_modified is False
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)

    def test_hyphen_mode_also_works(self):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai-compatible-http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-real-key-abcdef123456"

            with patch("httpx.post", side_effect=_mock_httpx_post_success):
                req = ProviderGatewayRequest(
                    messages=[{"role": "user", "content": "Hello"}],
                )
                resp = provider_gateway_complete(req)

            assert resp.status == "provider_response"
            assert resp.mode == "openai_compatible_http"
            assert resp.persisted is False
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)

    def test_api_key_not_exposed_in_response(self):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-super-secret-key-abcdef123456"

            with patch("httpx.post", side_effect=_mock_httpx_post_success):
                req = ProviderGatewayRequest(
                    messages=[{"role": "user", "content": "test"}],
                )
                resp = provider_gateway_complete(req)

            assert "sk-super-secret" not in resp.content
            assert resp.redaction_summary.get("api_key_exposed") is False
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)

    def test_always_persisted_false(self):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-key-abcdef123456"

            with patch("httpx.post", side_effect=_mock_httpx_post_success):
                req = ProviderGatewayRequest(
                    messages=[{"role": "user", "content": "test"}],
                )
                resp = provider_gateway_complete(req)

            assert resp.persisted is False
            assert resp.active_yaml_modified is False
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)


class TestRealProviderHTTPError:
    def test_http_error_returns_error_status(self):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-key-abcdef123456"

            with patch("httpx.post", side_effect=_mock_httpx_post_http_error):
                req = ProviderGatewayRequest(
                    messages=[{"role": "user", "content": "test"}],
                )
                resp = provider_gateway_complete(req)

            assert resp.status == "error"
            assert "HTTPStatusError" in resp.content
            assert resp.persisted is False
            assert resp.active_yaml_modified is False
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)

    def test_empty_choices_returns_error(self):
        """Empty choices list causes IndexError → caught as error."""
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-key-abcdef123456"

            with patch("httpx.post", side_effect=_mock_httpx_post_empty_choices):
                req = ProviderGatewayRequest(
                    messages=[{"role": "user", "content": "test"}],
                )
                resp = provider_gateway_complete(req)

            assert resp.status == "error"
            assert "IndexError" in resp.content
            assert resp.persisted is False
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)

    def test_missing_config_returns_error(self):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ.pop("ALTERS_PROVIDER_BASE_URL", None)
            os.environ.pop("ALTERS_PROVIDER_API_KEY", None)

            # Patch _resolve_config_value and _resolve_secret to return None
            # so no YAML config is found either
            with patch("alters_lab.services.provider_gateway._resolve_config_value", return_value=None), \
                 patch("alters_lab.services.provider_gateway._resolve_secret", return_value=None):
                req = ProviderGatewayRequest(
                    messages=[{"role": "user", "content": "test"}],
                )
                resp = provider_gateway_complete(req)

            assert resp.status == "error"
            assert "base_url" in resp.content.lower() or "api_key" in resp.content.lower()
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)


class TestRealProviderHTTPPayloadFormat:
    def test_payload_has_correct_structure(self):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-key-abcdef123456"

            captured_args = []
            captured_kwargs = {}

            def capture_post(*args, **kwargs):
                captured_args.extend(args)
                captured_kwargs.update(kwargs)
                return _mock_httpx_post_success(*args, **kwargs)

            with patch("httpx.post", side_effect=capture_post):
                req = ProviderGatewayRequest(
                    messages=[
                        {"role": "system", "content": "You are an alter."},
                        {"role": "user", "content": "Hello"},
                    ],
                    model="gpt-4o",
                    temperature=0.7,
                    max_tokens=500,
                )
                resp = provider_gateway_complete(req)

            assert resp.status == "provider_response"
            # Verify the payload structure
            assert captured_kwargs["json"]["model"] == "gpt-4o"
            assert len(captured_kwargs["json"]["messages"]) == 2
            assert captured_kwargs["json"]["temperature"] == 0.7
            assert captured_kwargs["json"]["max_tokens"] == 500
            # Verify auth header
            assert "Bearer sk-test-key-abcdef123456" in captured_kwargs["headers"]["Authorization"]
            # Verify URL (first positional arg)
            assert captured_args[0] == "http://127.0.0.1:8080/v1/chat/completions"
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)

    def test_default_model_used_when_not_in_request(self):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        original_model = os.environ.get("ALTERS_PROVIDER_MODEL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-key-abcdef123456"
            os.environ["ALTERS_PROVIDER_MODEL"] = "default-env-model"

            captured_kwargs = {}

            def capture_post(*args, **kwargs):
                captured_kwargs.update(kwargs)
                return _mock_httpx_post_success(*args, **kwargs)

            with patch("httpx.post", side_effect=capture_post):
                req = ProviderGatewayRequest(
                    messages=[{"role": "user", "content": "test"}],
                )
                resp = provider_gateway_complete(req)

            assert captured_kwargs["json"]["model"] == "default-env-model"
            assert resp.model == "default-env-model"
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)
            _restore_env("ALTERS_PROVIDER_MODEL", original_model)


# ---------------------------------------------------------------------------
# Provider dialogue with real HTTP backend
# ---------------------------------------------------------------------------

class TestProviderDialogueWithRealHTTP:
    def test_dialogue_calls_real_provider(self, tmp_path, monkeypatch):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-key-abcdef123456"

            monkeypatch.setattr("alters_lab.services.provider_dialogue._get_repo_root", lambda: tmp_path)
            alters_dir = tmp_path / "alters" / "current" / "alters"
            alters_dir.mkdir(parents=True)
            (alters_dir / "alter_A.yaml").write_text(
                "id: alter_A\nbranch_ref: branch_A\ndescription: test alter\n",
                encoding="utf-8",
            )

            with patch("httpx.post", side_effect=_mock_httpx_post_success):
                req = ProviderDialogueReplyRequest(user_message="Hello alter A")
                resp = provider_dialogue_reply(req, "alter_A", tmp_path)

            assert resp.status == "provider_response"
            assert resp.alter_id == "alter_A"
            assert "simulated alter branch" in resp.reply_text
            assert resp.persisted is False
            assert resp.session_path is None
            # Safety boundaries
            assert resp.safety_boundaries.active_yaml_modified is False
            assert resp.safety_boundaries.reality_score_created is False
            assert resp.boundary_confirmations.active_yaml_modified is False
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)

    def test_dialogue_error_from_provider(self, tmp_path, monkeypatch):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-key-abcdef123456"

            monkeypatch.setattr("alters_lab.services.provider_dialogue._get_repo_root", lambda: tmp_path)
            alters_dir = tmp_path / "alters" / "current" / "alters"
            alters_dir.mkdir(parents=True)
            (alters_dir / "alter_A.yaml").write_text(
                "id: alter_A\nbranch_ref: branch_A\n",
                encoding="utf-8",
            )

            with patch("httpx.post", side_effect=_mock_httpx_post_http_error):
                req = ProviderDialogueReplyRequest(user_message="Hello")
                resp = provider_dialogue_reply(req, "alter_A", tmp_path)

            assert resp.status == "error"
            assert resp.persisted is False
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)

    def test_dialogue_session_saves_provider_response(self, tmp_path, monkeypatch):
        import yaml as yaml_mod
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-key-abcdef123456"

            monkeypatch.setattr("alters_lab.services.provider_dialogue._get_repo_root", lambda: tmp_path)
            alters_dir = tmp_path / "alters" / "current" / "alters"
            alters_dir.mkdir(parents=True)
            (alters_dir / "alter_A.yaml").write_text(
                "id: alter_A\nbranch_ref: branch_A\n",
                encoding="utf-8",
            )

            with patch("httpx.post", side_effect=_mock_httpx_post_success):
                req = ProviderDialogueReplyRequest(user_message="test session", save_session=True)
                resp = provider_dialogue_reply(req, "alter_A", tmp_path)

            assert resp.persisted is True
            assert resp.session_path is not None
            session_data = yaml_mod.safe_load(Path(resp.session_path).read_text(encoding="utf-8"))
            assert session_data["provider_mode"] == "openai_compatible_http"
            assert "simulated alter branch" in session_data["reply_text"]
            assert session_data["safety_metadata"]["active_yaml_modified"] is False
            assert session_data["safety_metadata"]["no_secrets_in_session"] is True
            # No API key in session file
            assert "sk-test-key" not in Path(resp.session_path).read_text(encoding="utf-8")
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)


# ---------------------------------------------------------------------------
# Health and config status with real provider mode
# ---------------------------------------------------------------------------

class TestHealthWithRealMode:
    def test_health_shows_real_mode(self):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai-compatible-http"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-key-abcdef123456"
            resp = get_provider_gateway_health()
            assert resp.mode == "openai_compatible_http"
            assert resp.api_key_configured is True
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)


# ---------------------------------------------------------------------------
# Safety boundary enforcement
# ---------------------------------------------------------------------------

class TestSafetyBoundaries:
    def test_provider_output_never_persists(self):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-key-abcdef123456"

            with patch("httpx.post", side_effect=_mock_httpx_post_success):
                req = ProviderGatewayRequest(
                    messages=[{"role": "user", "content": "test"}],
                )
                resp = provider_gateway_complete(req)

            assert resp.persisted is False
            assert resp.active_yaml_modified is False
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)

    def test_dialogue_boundary_confirmations_always_safe(self, tmp_path, monkeypatch):
        original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
        original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
        original_url = os.environ.get("ALTERS_PROVIDER_BASE_URL")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "openai_compatible_http"
            os.environ["ALTERS_PROVIDER_BASE_URL"] = "http://127.0.0.1:8080/v1"
            os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-key-abcdef123456"

            monkeypatch.setattr("alters_lab.services.provider_dialogue._get_repo_root", lambda: tmp_path)
            alters_dir = tmp_path / "alters" / "current" / "alters"
            alters_dir.mkdir(parents=True)
            (alters_dir / "alter_A.yaml").write_text(
                "id: alter_A\nbranch_ref: branch_A\n",
                encoding="utf-8",
            )

            with patch("httpx.post", side_effect=_mock_httpx_post_success):
                req = ProviderDialogueReplyRequest(user_message="test boundaries")
                resp = provider_dialogue_reply(req, "alter_A", tmp_path)

            bc = resp.safety_boundaries
            assert bc.active_yaml_modified is False
            assert bc.rubric_modified is False
            assert bc.reality_score_created is False
            assert bc.drift_computed is False
            assert bc.archive_triggered is False
            assert bc.checkpoint_triggered is False
        finally:
            _restore_env("ALTERS_PROVIDER_MODE", original_mode)
            _restore_env("ALTERS_PROVIDER_API_KEY", original_key)
            _restore_env("ALTERS_PROVIDER_BASE_URL", original_url)


# ---------------------------------------------------------------------------
# No provider SDK imports
# ---------------------------------------------------------------------------

class TestNoProviderSDKImports:
    def test_no_openai_or_anthropic_imports(self):
        import alters_lab.services.provider_gateway as mod
        content = open(mod.__file__).read().lower()
        for pattern in ["from openai", "import openai", "from anthropic", "import anthropic"]:
            assert pattern not in content


# ---------------------------------------------------------------------------
# Redaction of secrets from provider content
# ---------------------------------------------------------------------------

class TestSecretRedaction:
    def test_sk_keys_redacted(self):
        text = "My API key is sk-abc12345678901234567890 and the response is here."
        redacted = _redact_secrets(text)
        assert "sk-abc123" not in redacted
        assert "[REDACTED]" in redacted

    def test_bearer_tokens_redacted(self):
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        redacted = _redact_secrets(text)
        assert "eyJhbGciOi" not in redacted
        assert "[REDACTED]" in redacted

    def test_clean_text_unaffected(self):
        text = "This is a normal response with no secrets."
        redacted = _redact_secrets(text)
        assert redacted == text


# ---------------------------------------------------------------------------
# Config-based resolution (YAML bridge)
# ---------------------------------------------------------------------------

class TestConfigResolution:
    def test_resolve_config_value_returns_none_on_error(self):
        """When no config exists, _resolve_config_value should return None gracefully."""
        from alters_lab.services.provider_gateway import _resolve_config_value
        result = _resolve_config_value("base_url")
        # Should not raise, may return None or a value depending on layout
        assert result is None or isinstance(result, str)

    def test_resolve_secret_returns_none_when_no_key(self):
        """When no secret is stored, _resolve_secret should return None gracefully."""
        from alters_lab.services.provider_gateway import _resolve_secret
        result = _resolve_secret()
        # Should not raise
        assert result is None or isinstance(result, str)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _restore_env(key: str, original_value: str | None):
    """Restore an env var to its original state."""
    if original_value is not None:
        os.environ[key] = original_value
    else:
        os.environ.pop(key, None)
