#!/usr/bin/env python3
"""Build a local Debian package for Alters Lab."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

PACKAGE_NAME = "alters-lab"
VERSION = "0.1.0"
ARCHITECTURE = "amd64"
MAINTAINER = "Charlie / Alters Lab"
DESCRIPTION = "Local personal calibration app for Alters Lab"

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
    "alters_lab_api.egg-info",
}
EXCLUDED_FILE_NAMES = {".env", ".env.local", "secrets.yaml", "config.yaml"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".deb"}


@dataclass(frozen=True)
class DebBuildPaths:
    repo_root: Path
    staging_root: Path
    package_root: Path
    debian_dir: Path
    opt_root: Path
    api_root: Path
    web_dist_root: Path
    usr_bin: Path
    output_dir: Path
    output_deb: Path


def resolve_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def build_paths(repo_root: Path, version: str = VERSION, architecture: str = ARCHITECTURE) -> DebBuildPaths:
    staging_root = repo_root / "build" / "deb" / PACKAGE_NAME
    package_root = staging_root
    output_dir = repo_root / "dist" / "deb"
    return DebBuildPaths(
        repo_root=repo_root,
        staging_root=staging_root,
        package_root=package_root,
        debian_dir=package_root / "DEBIAN",
        opt_root=package_root / "opt" / PACKAGE_NAME,
        api_root=package_root / "opt" / PACKAGE_NAME / "apps" / "api",
        web_dist_root=package_root / "opt" / PACKAGE_NAME / "web" / "dist",
        usr_bin=package_root / "usr" / "bin",
        output_dir=output_dir,
        output_deb=output_dir / f"{PACKAGE_NAME}_{version}_{architecture}.deb",
    )


def render_control(version: str = VERSION, architecture: str = ARCHITECTURE) -> str:
    return (
        f"Package: {PACKAGE_NAME}\n"
        f"Version: {version}\n"
        "Section: utils\n"
        "Priority: optional\n"
        f"Architecture: {architecture}\n"
        "Depends: python3\n"
        f"Maintainer: {MAINTAINER}\n"
        f"Description: {DESCRIPTION}\n"
        " Single-user local application package for running Alters Lab from /opt/alters-lab.\n"
    )


def launcher_script() -> str:
    return """#!/bin/sh
set -eu
APP_ROOT=/opt/alters-lab
export ALTERS_LAB_MODE="${ALTERS_LAB_MODE:-packaged}"
export PYTHONPATH="$APP_ROOT/apps/api/src${PYTHONPATH:+:$PYTHONPATH}"
if [ -x "$APP_ROOT/.venv/bin/python" ]; then
  exec "$APP_ROOT/.venv/bin/python" -m alters_lab.cli "$@"
fi
exec python3 -m alters_lab.cli "$@"
"""


def is_excluded(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return True
    if path.name in EXCLUDED_FILE_NAMES:
        return True
    if path.suffix in EXCLUDED_SUFFIXES:
        return True
    if "alters/product" in path.as_posix():
        return True
    return False


def copy_tree_filtered(source: Path, target: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(source)
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if is_excluded(relative):
            if path.is_dir():
                continue
            continue
        destination = target / relative
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)


def clean_paths(paths: DebBuildPaths) -> None:
    if paths.staging_root.exists():
        shutil.rmtree(paths.staging_root)
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    paths.debian_dir.mkdir(parents=True, exist_ok=True)
    paths.usr_bin.mkdir(parents=True, exist_ok=True)
    paths.opt_root.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def build_frontend(repo_root: Path) -> None:
    web_dir = repo_root / "apps" / "web"
    run(["npm", "install"], web_dir)
    run(["npm", "run", "build"], web_dir)


def write_packaging_files(paths: DebBuildPaths) -> None:
    paths.debian_dir.mkdir(parents=True, exist_ok=True)
    (paths.debian_dir / "control").write_text(render_control(), encoding="utf-8")

    packaging_dir = paths.repo_root / "packaging" / "deb"
    for script_name in ["postinst", "prerm", "postrm"]:
        source = packaging_dir / script_name
        if source.exists():
            target = paths.debian_dir / script_name
            shutil.copy2(source, target)
            target.chmod(0o755)

    launcher = paths.usr_bin / PACKAGE_NAME
    launcher.write_text(launcher_script(), encoding="utf-8")
    launcher.chmod(0o755)


def stage_app(paths: DebBuildPaths) -> None:
    api_source = paths.repo_root / "apps" / "api"
    web_dist = paths.repo_root / "apps" / "web" / "dist"
    if not web_dist.exists():
        raise FileNotFoundError("frontend dist missing; run npm run build first")

    copy_tree_filtered(api_source / "src", paths.api_root / "src")
    for file_name in ["pyproject.toml", "README.md"]:
        source = api_source / file_name
        if source.exists():
            shutil.copy2(source, paths.api_root / file_name)
    copy_tree_filtered(web_dist, paths.web_dist_root)


def build_venv(paths: DebBuildPaths) -> None:
    venv_path = paths.opt_root / ".venv"
    run(["python3", "-m", "venv", str(venv_path)], paths.repo_root)
    run([str(venv_path / "bin" / "python"), "-m", "pip", "install", "--upgrade", "pip"], paths.repo_root)
    run([str(venv_path / "bin" / "python"), "-m", "pip", "install", str(paths.api_root)], paths.repo_root)


def assert_package_safety(paths: DebBuildPaths) -> None:
    forbidden_fragments = [
        "node_modules",
        ".env",
        "alters/product",
        ".config/alters-lab",
        ".local/share/alters-lab",
        ".local/state/alters-lab",
        "secrets.yaml",
    ]
    for path in paths.package_root.rglob("*"):
        rel = path.relative_to(paths.package_root).as_posix()
        for fragment in forbidden_fragments:
            if fragment in rel:
                raise RuntimeError(f"forbidden package path: {rel}")


def build_deb(paths: DebBuildPaths) -> Path:
    if paths.output_deb.exists():
        paths.output_deb.unlink()
    run(["dpkg-deb", "--root-owner-group", "--build", str(paths.package_root), str(paths.output_deb)], paths.repo_root)
    return paths.output_deb


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Alters Lab Debian package")
    parser.add_argument("--skip-frontend-build", action="store_true")
    parser.add_argument("--skip-venv", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = resolve_repo_root()
    paths = build_paths(repo_root)
    clean_paths(paths)
    if not args.skip_frontend_build:
        build_frontend(repo_root)
    stage_app(paths)
    write_packaging_files(paths)
    if not args.skip_venv:
        build_venv(paths)
    assert_package_safety(paths)
    output = build_deb(paths)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
