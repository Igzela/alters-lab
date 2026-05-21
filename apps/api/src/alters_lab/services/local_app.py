"""Unified local app server helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from alters_lab.services.runtime_layout import RuntimeLayout, default_config, load_user_config_if_exists, redacted_config_status, resolve_runtime_layout


API_PREFIXES = {
    "action-alignment",
    "alter-dialogue",
    "alter-recommendation",
    "alters",
    "archive-mechanism",
    "behavior-validation",
    "branches",
    "calibration-loop",
    "checkpoint-regeneration",
    "cycle-summary",
    "docs",
    "draft-review",
    "evidence",
    "generation-drafts",
    "health",
    "local-app",
    "obsidian-weekly-note",
    "openapi.json",
    "p6-data-retention",
    "p6-provider-policy",
    "pattern-review",
    "phase3-closeout",
    "phase4-closeout",
    "phase5-closeout",
    "phase6-closeout",
    "product",
    "promotion-execution-gate",
    "promotion-live-execution",
    "promotion-orchestration",
    "provider-dialogue",
    "provider-gateway",
    "redoc",
    "rubric-delta",
    "runtime-layout",
    "self-deception-challenge",
    "snapshot-intake",
    "storage-boundary",
    "user-workflow",
    "weekly-reminder",
    "weekly-review",
}


def resolve_frontend_dist(layout: RuntimeLayout | None = None) -> Path:
    resolved_layout = layout or resolve_runtime_layout()
    if resolved_layout.mode == "packaged":
        return resolved_layout.app_root / "web" / "dist"
    repo_root = resolved_layout.repo_root or resolve_runtime_layout(mode="dev").repo_root
    if repo_root is None:
        return resolved_layout.app_root / "web" / "dist"
    return repo_root / "apps" / "web" / "dist"


def frontend_available(layout: RuntimeLayout | None = None) -> bool:
    dist = resolve_frontend_dist(layout)
    return dist.is_dir() and (dist / "index.html").is_file()


def build_local_app_status(layout: RuntimeLayout | None = None) -> dict[str, Any]:
    resolved_layout = layout or resolve_runtime_layout()
    config = load_user_config_if_exists(resolved_layout) or default_config(resolved_layout)
    config_status = redacted_config_status(config)
    server = config.get("server") if isinstance(config.get("server"), dict) else {}
    dist = resolve_frontend_dist(resolved_layout)
    return {
        "status": "ok",
        "backend_ready": True,
        "frontend_available": frontend_available(resolved_layout),
        "frontend_dist_path": str(dist),
        "runtime_mode": resolved_layout.mode,
        "host": server.get("host", "127.0.0.1"),
        "port": server.get("port", 18790),
        "api_routes_available": True,
        "provider_mode": config_status["provider_mode"],
        "secrets_redacted": True,
        "p6_behavior_validated": False,
        "p6_sealed": False,
        "active_yaml_write_allowed": resolved_layout.active_yaml_write_allowed,
        "rubric_write_allowed": resolved_layout.rubric_write_allowed,
    }


def safe_dist_file(dist: Path, relative_path: str) -> Path:
    candidate = (dist / relative_path).resolve()
    dist_root = dist.resolve()
    if not candidate.is_relative_to(dist_root) or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Static asset not found")
    return candidate


def should_block_spa_fallback(path: str) -> bool:
    first = path.split("/", 1)[0]
    return first in API_PREFIXES


def frontend_missing_response(layout: RuntimeLayout | None = None) -> HTMLResponse:
    dist = resolve_frontend_dist(layout)
    return HTMLResponse(
        content=(
            "<!doctype html><html><head><title>Alters Lab</title></head>"
            "<body><h1>Alters Lab API is running</h1>"
            f"<p>Frontend build not found at {dist}.</p></body></html>"
        ),
        status_code=503,
    )


def frontend_index_response(layout: RuntimeLayout | None = None) -> FileResponse | HTMLResponse:
    resolved_layout = layout or resolve_runtime_layout()
    if not frontend_available(resolved_layout):
        return frontend_missing_response(resolved_layout)
    return FileResponse(resolve_frontend_dist(resolved_layout) / "index.html")


def configure_frontend_static(app: FastAPI) -> None:
    @app.get("/", include_in_schema=False)
    def serve_frontend_root():
        return frontend_index_response()

    @app.get("/assets/{asset_path:path}", include_in_schema=False)
    def serve_frontend_asset(asset_path: str):
        layout = resolve_runtime_layout()
        dist = resolve_frontend_dist(layout)
        if not frontend_available(layout):
            raise HTTPException(status_code=404, detail="Frontend build not available")
        return FileResponse(safe_dist_file(dist / "assets", asset_path))

    @app.get("/{frontend_path:path}", include_in_schema=False)
    def serve_frontend_route(frontend_path: str):
        if should_block_spa_fallback(frontend_path):
            raise HTTPException(status_code=404, detail="API route not found")
        return frontend_index_response()

    @app.api_route(
        "/{frontend_path:path}",
        methods=["POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        include_in_schema=False,
    )
    def reject_non_get_frontend_route(frontend_path: str):
        raise HTTPException(status_code=404, detail="Route not found")
