"""Tests for local provider configuration service."""

from __future__ import annotations

import stat
from pathlib import Path

import yaml

from alters_lab.schemas.provider_config import ProviderConfigTestRequest, ProviderConfigUpdateRequest
from alters_lab.services.provider_config import (
    ProviderConfigError,
    delete_provider_secret,
    get_provider_config,
    get_provider_status,
    store_provider_secret,
    test_provider_config as run_provider_config_test,
    update_provider_config,
)
from alters_lab.services.runtime_layout import RuntimeLayout, resolve_runtime_layout


def _layout(tmp_path: Path) -> RuntimeLayout:
    repo = tmp_path / "repo"
    repo.mkdir()
    return resolve_runtime_layout(
        mode="dev",
        repo_root=repo,
        config_dir=tmp_path / "config",
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
    )


def test_default_provider_mode_disabled(tmp_path: Path):
    status = get_provider_status(_layout(tmp_path))

    assert status.provider_mode == "disabled"
    assert status.configured is True
    assert status.api_key_configured is False
    assert status.secrets_redacted is True


def test_get_config_never_returns_api_key(tmp_path: Path):
    layout = _layout(tmp_path)
    store_provider_secret("test-key-not-real", "secrets_yaml_fallback", "store-secret", layout)

    config = get_provider_config(layout).model_dump()

    assert "api_key" not in config
    assert "test-key-not-real" not in str(config)


def test_post_config_writes_config_only(tmp_path: Path):
    layout = _layout(tmp_path)
    update_provider_config(
        ProviderConfigUpdateRequest(
            mode="mock",
            model="mock-model",
            timeout_seconds=30,
            secret_storage="secrets_yaml_fallback",
        ),
        layout,
    )

    config = yaml.safe_load(layout.config_path.read_text(encoding="utf-8"))
    assert config["provider"]["mode"] == "mock"
    assert not layout.secrets_path.exists()


def test_disabled_and_mock_do_not_require_key(tmp_path: Path):
    layout = _layout(tmp_path)
    update_provider_config(ProviderConfigUpdateRequest(mode="disabled"), layout)
    assert get_provider_status(layout).configured is True

    update_provider_config(ProviderConfigUpdateRequest(mode="mock"), layout)
    assert get_provider_status(layout).configured is True


def test_openai_compatible_requires_explicit_configuration(tmp_path: Path):
    layout = _layout(tmp_path)

    try:
        update_provider_config(
            ProviderConfigUpdateRequest(
                mode="openai-compatible-http",
                base_url="http://127.0.0.1:9999/v1",
                model="test-model",
            ),
            layout,
        )
    except ProviderConfigError as exc:
        assert "explicit_user_configuration" in str(exc)
    else:
        raise AssertionError("expected ProviderConfigError")


def test_openai_compatible_configured_requires_base_url_model_and_secret(tmp_path: Path):
    layout = _layout(tmp_path)
    update_provider_config(
        ProviderConfigUpdateRequest(
            mode="openai-compatible-http",
            base_url="http://127.0.0.1:9999/v1",
            model="test-model",
            secret_storage="secrets_yaml_fallback",
            explicit_user_configuration=True,
        ),
        layout,
    )

    assert get_provider_status(layout).configured is False
    store_provider_secret("test-key-not-real", "secrets_yaml_fallback", "store-secret", layout)
    status = get_provider_status(layout)
    assert status.configured is True
    assert status.base_url_configured is True
    assert status.model_configured is True
    assert status.api_key_configured is True


def test_store_secret_fallback_creates_0600_file(tmp_path: Path):
    layout = _layout(tmp_path)
    response = store_provider_secret("test-key-not-real", "secrets_yaml_fallback", "store-secret", layout)

    assert response.api_key_configured is True
    assert response.secret_storage == "secrets_yaml_fallback"
    assert stat.S_IMODE(layout.secrets_path.stat().st_mode) == 0o600
    assert "test-key-not-real" in layout.secrets_path.read_text(encoding="utf-8")


def test_store_secret_response_never_returns_key(tmp_path: Path):
    response = store_provider_secret("test-key-not-real", "secrets_yaml_fallback", "store-secret", _layout(tmp_path))

    assert "test-key-not-real" not in response.model_dump_json()
    assert response.secrets_redacted is True


def test_delete_secret_preserves_config(tmp_path: Path):
    layout = _layout(tmp_path)
    update_provider_config(ProviderConfigUpdateRequest(mode="mock", model="mock-model"), layout)
    config_before = layout.config_path.read_text(encoding="utf-8")

    store_provider_secret("test-key-not-real", "secrets_yaml_fallback", "store-secret", layout)
    response = delete_provider_secret("delete-secret", "secrets_yaml_fallback", layout)

    assert response.api_key_configured is False
    assert layout.config_path.read_text(encoding="utf-8") == config_before
    assert get_provider_status(layout).api_key_configured is False


def test_provider_config_test_disabled_skips(tmp_path: Path):
    response = run_provider_config_test(ProviderConfigTestRequest(), _layout(tmp_path))

    assert response.status == "skipped"
    assert response.provider_ready is False
    assert response.network_call_made is False


def test_provider_config_test_mock_ok_without_network(tmp_path: Path):
    layout = _layout(tmp_path)
    update_provider_config(ProviderConfigUpdateRequest(mode="mock"), layout)

    response = run_provider_config_test(ProviderConfigTestRequest(), layout)

    assert response.status == "ok"
    assert response.provider_ready is True
    assert response.network_call_made is False


def test_provider_config_test_openai_dry_run_without_network(tmp_path: Path):
    layout = _layout(tmp_path)
    update_provider_config(
        ProviderConfigUpdateRequest(
            mode="openai-compatible-http",
            base_url="http://127.0.0.1:9999/v1",
            model="test-model",
            secret_storage="secrets_yaml_fallback",
            explicit_user_configuration=True,
        ),
        layout,
    )

    misconfigured = run_provider_config_test(ProviderConfigTestRequest(), layout)
    assert misconfigured.status == "misconfigured"
    assert misconfigured.network_call_made is False

    store_provider_secret("test-key-not-real", "secrets_yaml_fallback", "store-secret", layout)
    configured = run_provider_config_test(ProviderConfigTestRequest(), layout)
    assert configured.status == "configured"
    assert configured.provider_ready is True
    assert configured.network_call_made is False


def test_live_check_not_implemented_without_network(tmp_path: Path):
    layout = _layout(tmp_path)
    update_provider_config(
        ProviderConfigUpdateRequest(
            mode="openai-compatible-http",
            base_url="http://127.0.0.1:9999/v1",
            model="test-model",
            explicit_user_configuration=True,
        ),
        layout,
    )

    response = run_provider_config_test(ProviderConfigTestRequest(live_check=True), layout)

    assert response.status == "not_implemented"
    assert response.network_call_made is False


def test_p6_flags_remain_false(tmp_path: Path):
    status = get_provider_status(_layout(tmp_path))

    assert status.behavior_validated is False
    assert status.p6_sealed is False
    assert status.provider_output_can_write_active_yaml is False
    assert status.provider_output_can_generate_reality_score is False
