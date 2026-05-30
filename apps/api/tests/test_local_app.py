"""Service tests for P7 unified local app server."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from alters_lab.services.local_app import (
    build_local_app_status,
    frontend_available,
    resolve_frontend_dist,
    safe_dist_file,
    should_block_spa_fallback,
)
from alters_lab.services.runtime_layout import resolve_runtime_layout


def test_resolve_frontend_dist_dev_uses_repo_web_dist(tmp_path):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)

    assert resolve_frontend_dist(layout) == tmp_path / "apps" / "web" / "dist"


def test_resolve_frontend_dist_packaged_uses_app_root_web_dist(tmp_path):
    layout = resolve_runtime_layout(mode="packaged", app_root=tmp_path / "opt" / "alters-lab")

    assert resolve_frontend_dist(layout) == tmp_path / "opt" / "alters-lab" / "web" / "dist"


def test_frontend_available_requires_index_html(tmp_path):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)

    assert frontend_available(layout) is False
    dist = tmp_path / "apps" / "web" / "dist"
    dist.mkdir(parents=True)
    assert frontend_available(layout) is False
    (dist / "index.html").write_text("<html>ok</html>", encoding="utf-8")
    assert frontend_available(layout) is True


def test_build_local_app_status_safe_defaults(tmp_path):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)

    status = build_local_app_status(layout)

    assert status["backend_ready"] is True
    assert status["frontend_available"] is False
    assert status["runtime_mode"] == "dev"
    assert status["host"] == "127.0.0.1"
    assert status["port"] == 18790
    assert status["api_routes_available"] is True
    assert status["provider_mode"] == "disabled"
    assert status["secrets_redacted"] is True
    assert status["behavior_validated"] is False
    assert status["p6_sealed"] is False
    assert status["active_yaml_write_allowed"] is False
    assert status["rubric_write_allowed"] is False


def test_safe_dist_file_blocks_path_traversal(tmp_path):
    dist = tmp_path / "dist" / "assets"
    dist.mkdir(parents=True)
    (tmp_path / "dist" / "secret.txt").write_text("secret", encoding="utf-8")

    with pytest.raises(HTTPException):
        safe_dist_file(dist, "../secret.txt")


def test_safe_dist_file_returns_asset_inside_dist(tmp_path):
    dist = tmp_path / "dist" / "assets"
    dist.mkdir(parents=True)
    asset = dist / "app.js"
    asset.write_text("console.log('ok')", encoding="utf-8")

    assert safe_dist_file(dist, "app.js") == asset.resolve()


def test_spa_fallback_blocks_api_prefixes():
    assert should_block_spa_fallback("runtime-layout/status") is True
    assert should_block_spa_fallback("local-app/status") is True
    assert should_block_spa_fallback("weekly-review/start") is True
    assert should_block_spa_fallback("settings") is False
