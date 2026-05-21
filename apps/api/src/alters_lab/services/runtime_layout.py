"""Runtime layout resolver for dev and packaged local app modes."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml


RuntimeMode = Literal["dev", "packaged"]

APP_NAME = "alters-lab"
DEFAULT_PACKAGED_APP_ROOT = Path("/opt/alters-lab")
DEFAULT_SERVER_HOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 18790


@dataclass(frozen=True)
class RuntimeLayout:
    mode: RuntimeMode
    app_root: Path
    repo_root: Path | None
    config_dir: Path
    config_path: Path
    data_dir: Path
    product_data_dir: Path
    state_dir: Path
    logs_dir: Path
    secrets_path: Path
    provider_secrets_preferred: str = "system_keyring"
    active_yaml_write_allowed: bool = False
    rubric_write_allowed: bool = False
    provider_output_persists_by_default: bool = False
    provider_output_can_write_active_yaml: bool = False


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def normalize_runtime_mode(value: str | None) -> RuntimeMode | None:
    if value is None or value == "":
        return None
    normalized = value.strip().lower()
    if normalized not in {"dev", "packaged"}:
        raise ValueError(f"Invalid runtime mode: {value}")
    return normalized  # type: ignore[return-value]


def resolve_runtime_mode(mode: str | None = None, app_root: Path | None = None) -> RuntimeMode:
    explicit = normalize_runtime_mode(mode)
    if explicit is not None:
        return explicit
    env_mode = normalize_runtime_mode(os.environ.get("ALTERS_LAB_MODE"))
    if env_mode is not None:
        return env_mode
    marker_root = app_root or DEFAULT_PACKAGED_APP_ROOT
    if marker_root == DEFAULT_PACKAGED_APP_ROOT and marker_root.exists():
        return "packaged"
    return "dev"


def resolve_runtime_layout(
    mode: str | None = None,
    repo_root: Path | None = None,
    app_root: Path | None = None,
    config_dir: Path | None = None,
    data_dir: Path | None = None,
    state_dir: Path | None = None,
) -> RuntimeLayout:
    env_app_root = os.environ.get("ALTERS_LAB_APP_ROOT")
    resolved_app_root_override = app_root or (Path(env_app_root).expanduser() if env_app_root else None)
    resolved_mode = resolve_runtime_mode(mode, resolved_app_root_override)
    resolved_repo_root = repo_root.resolve() if repo_root is not None else get_repo_root()

    if resolved_mode == "dev":
        resolved_app_root = (resolved_app_root_override or resolved_repo_root).resolve()
        resolved_config_dir = (config_dir or (resolved_repo_root / "alters" / "product" / "config")).resolve()
        resolved_data_dir = (data_dir or resolved_repo_root).resolve()
        product_data_dir = resolved_data_dir / "alters" / "product"
        resolved_state_dir = (state_dir or (resolved_repo_root / "alters" / "product" / "state")).resolve()
    else:
        resolved_app_root = (resolved_app_root_override or DEFAULT_PACKAGED_APP_ROOT).resolve()
        resolved_config_dir = (config_dir or (Path.home() / ".config" / APP_NAME)).expanduser().resolve()
        resolved_data_dir = (data_dir or (Path.home() / ".local" / "share" / APP_NAME)).expanduser().resolve()
        product_data_dir = resolved_data_dir / "product"
        resolved_state_dir = (state_dir or (Path.home() / ".local" / "state" / APP_NAME)).expanduser().resolve()
        resolved_repo_root = repo_root.resolve() if repo_root is not None else None

    return RuntimeLayout(
        mode=resolved_mode,
        app_root=resolved_app_root,
        repo_root=resolved_repo_root,
        config_dir=resolved_config_dir,
        config_path=resolved_config_dir / "config.yaml",
        data_dir=resolved_data_dir,
        product_data_dir=product_data_dir,
        state_dir=resolved_state_dir,
        logs_dir=resolved_state_dir / "logs",
        secrets_path=resolved_config_dir / "secrets.yaml",
    )


def default_config(layout: RuntimeLayout | None = None, mode: str | None = None) -> dict[str, Any]:
    resolved_layout = layout or resolve_runtime_layout(mode=mode)
    return {
        "version": 1,
        "mode": resolved_layout.mode,
        "server": {
            "host": DEFAULT_SERVER_HOST,
            "port": DEFAULT_SERVER_PORT,
            "open_browser_on_start": True,
        },
        "paths": {
            "data_dir": str(resolved_layout.data_dir),
            "state_dir": str(resolved_layout.state_dir),
        },
        "provider": {
            "mode": "disabled",
            "openai_compatible_http": {
                "base_url": None,
                "model": None,
                "timeout_seconds": 60,
            },
            "secrets": {
                "storage": "keyring",
                "key_name": "alters-lab/provider-api-key",
            },
        },
        "safety": {
            "active_yaml_write_allowed": False,
            "rubric_write_allowed": False,
            "provider_output_persists_by_default": False,
            "provider_output_can_write_active_yaml": False,
        },
    }


def ensure_user_config(layout: RuntimeLayout) -> Path:
    layout.config_dir.mkdir(parents=True, exist_ok=True)
    if not layout.config_path.exists():
        write_user_config(layout, default_config(layout))
    return layout.config_path


def load_user_config(layout: RuntimeLayout) -> dict[str, Any]:
    ensure_user_config(layout)
    data = yaml.safe_load(layout.config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Runtime config is not a mapping: {layout.config_path}")
    return data


def load_user_config_if_exists(layout: RuntimeLayout) -> dict[str, Any] | None:
    if not layout.config_path.exists():
        return None
    data = yaml.safe_load(layout.config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Runtime config is not a mapping: {layout.config_path}")
    return data


def write_user_config(layout: RuntimeLayout, config: dict[str, Any]) -> Path:
    layout.config_dir.mkdir(parents=True, exist_ok=True)
    layout.config_path.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return layout.config_path


def ensure_secrets_fallback_file(layout: RuntimeLayout) -> Path:
    layout.config_dir.mkdir(parents=True, exist_ok=True)
    if not layout.secrets_path.exists():
        layout.secrets_path.write_text(yaml.safe_dump({"version": 1}, sort_keys=False), encoding="utf-8")
        layout.secrets_path.chmod(0o600)
    else:
        layout.secrets_path.chmod(0o600)
    return layout.secrets_path


def redacted_config_status(config: dict[str, Any]) -> dict[str, Any]:
    provider = config.get("provider") if isinstance(config.get("provider"), dict) else {}
    secrets = provider.get("secrets") if isinstance(provider.get("secrets"), dict) else {}
    return {
        "provider_mode": provider.get("mode", "disabled"),
        "secrets_storage": secrets.get("storage", "keyring"),
        "secrets_redacted": True,
    }
