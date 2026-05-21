"""Read-only runtime layout routes for local app preparation."""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.runtime_layout import (
    RuntimeLayoutEnsureConfigResponse,
    RuntimeLayoutHealthResponse,
    RuntimeLayoutStatusResponse,
)
from alters_lab.services.runtime_layout import (
    default_config,
    ensure_user_config,
    load_user_config_if_exists,
    redacted_config_status,
    resolve_runtime_layout,
)

router = APIRouter(prefix="/runtime-layout", tags=["runtime-layout"])


@router.get("/health", response_model=RuntimeLayoutHealthResponse)
def health():
    return RuntimeLayoutHealthResponse()


@router.get("/status", response_model=RuntimeLayoutStatusResponse)
def status():
    layout = resolve_runtime_layout()
    config = load_user_config_if_exists(layout) or default_config(layout)
    config_status = redacted_config_status(config)
    return RuntimeLayoutStatusResponse(
        mode=layout.mode,
        config_path=str(layout.config_path),
        data_dir=str(layout.data_dir),
        product_data_dir=str(layout.product_data_dir),
        logs_dir=str(layout.logs_dir),
        provider_mode=config_status["provider_mode"],
        secrets_storage=config_status["secrets_storage"],
        secrets_redacted=config_status["secrets_redacted"],
        active_yaml_write_allowed=layout.active_yaml_write_allowed,
        rubric_write_allowed=layout.rubric_write_allowed,
        provider_output_persists_by_default=layout.provider_output_persists_by_default,
        provider_output_can_write_active_yaml=layout.provider_output_can_write_active_yaml,
    )


@router.post("/ensure-config", response_model=RuntimeLayoutEnsureConfigResponse)
def ensure_config():
    layout = resolve_runtime_layout()
    path = ensure_user_config(layout)
    return RuntimeLayoutEnsureConfigResponse(config_path=str(path))
