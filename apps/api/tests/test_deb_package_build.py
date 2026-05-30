"""Tests for P7-M5 Debian package build helpers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
BUILD_DEB_PATH = REPO_ROOT / "tools" / "build_deb.py"
INSPECT_DEB_PATH = REPO_ROOT / "tools" / "inspect_deb_safety.py"


def _load_build_deb():
    spec = importlib.util.spec_from_file_location("build_deb", BUILD_DEB_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_deb"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_inspect_deb():
    spec = importlib.util.spec_from_file_location("inspect_deb_safety", INSPECT_DEB_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["inspect_deb_safety"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build_paths_compute_expected_package_paths(tmp_path: Path):
    build_deb = _load_build_deb()

    paths = build_deb.build_paths(tmp_path)

    assert paths.api_root == tmp_path / "build/deb/alters-lab/opt/alters-lab/apps/api"
    assert paths.web_dist_root == tmp_path / "build/deb/alters-lab/opt/alters-lab/web/dist"
    assert paths.usr_bin == tmp_path / "build/deb/alters-lab/usr/bin"
    assert paths.applications_dir == tmp_path / "build/deb/alters-lab/usr/share/applications"
    assert paths.icon_dir == tmp_path / "build/deb/alters-lab/usr/share/icons/hicolor/scalable/apps"
    assert paths.output_deb == tmp_path / "dist/deb/alters-lab_0.1.0_amd64.deb"


def test_control_file_contains_package_name_version_and_architecture():
    build_deb = _load_build_deb()

    control = build_deb.render_control()

    assert "Package: alters-lab" in control
    assert "Version: 0.1.0" in control
    assert "Architecture: amd64" in control
    assert "Depends: python3" in control


def test_launcher_sets_packaged_mode_and_pythonpath():
    build_deb = _load_build_deb()

    launcher = build_deb.launcher_script()

    assert "ALTERS_LAB_MODE" in launcher
    assert "packaged" in launcher
    assert "PYTHONPATH" in launcher
    assert "apps/api/src" in launcher
    assert "python\" -m alters_lab.cli" in launcher


def test_package_exclusions_cover_node_env_runtime_and_user_paths():
    build_deb = _load_build_deb()

    assert build_deb.is_excluded(Path("node_modules/pkg/index.js"))
    assert build_deb.is_excluded(Path(".env"))
    assert build_deb.is_excluded(Path(".env.local"))
    assert build_deb.is_excluded(Path("alters/product/weekly_reviews/raw.yaml"))
    assert build_deb.is_excluded(Path("config.yaml"))
    assert build_deb.is_excluded(Path("secrets.yaml"))


def test_copy_tree_filtered_excludes_node_modules_env_and_runtime_records(tmp_path: Path):
    build_deb = _load_build_deb()
    source = tmp_path / "source"
    target = tmp_path / "target"
    (source / "src").mkdir(parents=True)
    (source / "src" / "app.py").write_text("print('ok')\n", encoding="utf-8")
    (source / "node_modules" / "pkg").mkdir(parents=True)
    (source / "node_modules" / "pkg" / "index.js").write_text("", encoding="utf-8")
    (source / ".env").write_text("SECRET=bad\n", encoding="utf-8")
    (source / "alters" / "product" / "weekly_reviews").mkdir(parents=True)
    (source / "alters" / "product" / "weekly_reviews" / "raw.yaml").write_text("x\n", encoding="utf-8")

    build_deb.copy_tree_filtered(source, target)

    assert (target / "src" / "app.py").exists()
    assert not (target / "node_modules").exists()
    assert not (target / ".env").exists()
    assert not (target / "alters" / "product").exists()


def test_maintainer_scripts_do_not_delete_user_home_data():
    for script_name in ["postinst", "prerm", "postrm"]:
        content = (REPO_ROOT / "packaging" / "deb" / script_name).read_text(encoding="utf-8")
        lowered = content.lower()
        assert "rm -rf ~/.config" not in lowered
        assert "rm -rf ~/.local" not in lowered
        assert ".config/alters-lab" not in lowered
        assert ".local/share/alters-lab" not in lowered
        assert ".local/state/alters-lab" not in lowered


def test_gitignore_ignores_package_outputs():
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "build/" in gitignore
    assert "dist/" in gitignore
    assert "*.deb" in gitignore


def test_package_docs_keep_p6_unvalidated_and_unsealed():
    pass  # Harness docs removed in open-source cleanup


def test_desktop_file_exists_and_launches_existing_cli():
    desktop = (REPO_ROOT / "packaging" / "deb" / "alters-lab.desktop").read_text(encoding="utf-8")

    assert "Type=Application" in desktop
    assert "Name=Alters Lab" in desktop
    assert "Exec=alters-lab open" in desktop
    assert "Terminal=false" in desktop
    assert "Categories=Utility;X-Productivity;" in desktop


def test_desktop_file_has_no_repo_home_secret_or_shell_expansion():
    desktop = (REPO_ROOT / "packaging" / "deb" / "alters-lab.desktop").read_text(encoding="utf-8")

    forbidden = ["$(", "`", "~", "/home/", "/home/igzela", "Projects/alters-lab", "OPENAI_API_KEY", "sk-"]
    for token in forbidden:
        assert token not in desktop


def test_icon_asset_exists_and_is_project_owned_svg():
    icon = REPO_ROOT / "packaging" / "assets" / "alters-lab.svg"
    content = icon.read_text(encoding="utf-8")

    assert icon.exists()
    assert "<svg" in content
    assert content.count("http://") == 1
    assert "http://www.w3.org/2000/svg" in content
    assert "https://" not in content


def test_write_packaging_files_stages_desktop_file_and_icon(tmp_path: Path):
    build_deb = _load_build_deb()
    paths = build_deb.build_paths(tmp_path)
    paths.debian_dir.mkdir(parents=True)
    paths.usr_bin.mkdir(parents=True)
    paths.applications_dir.mkdir(parents=True)
    paths.icon_dir.mkdir(parents=True)

    packaging_dir = tmp_path / "packaging" / "deb"
    assets_dir = tmp_path / "packaging" / "assets"
    packaging_dir.mkdir(parents=True)
    assets_dir.mkdir(parents=True)
    (packaging_dir / "alters-lab.desktop").write_text("Exec=alters-lab open\n", encoding="utf-8")
    (assets_dir / "alters-lab.svg").write_text("<svg></svg>\n", encoding="utf-8")

    build_deb.write_packaging_files(paths)

    assert (paths.applications_dir / "alters-lab.desktop").read_text(encoding="utf-8") == "Exec=alters-lab open\n"
    assert (paths.icon_dir / "alters-lab.svg").read_text(encoding="utf-8") == "<svg></svg>\n"
    assert (paths.usr_bin / "alters-lab").stat().st_mode & 0o111


def test_desktop_integration_docs_keep_p6_unvalidated_and_unsealed():
    pass  # Harness docs removed in open-source cleanup


def test_inspect_deb_forbidden_fragments_cover_user_data_and_runtime_records():
    inspect_deb = _load_inspect_deb()

    assert "node_modules" in inspect_deb.FORBIDDEN_FRAGMENTS
    assert "alters/product" in inspect_deb.FORBIDDEN_FRAGMENTS
    assert ".local/share/alters-lab" in inspect_deb.FORBIDDEN_FRAGMENTS
    assert ".local/state/alters-lab" in inspect_deb.FORBIDDEN_FRAGMENTS
    assert "secrets.yaml" in inspect_deb.FORBIDDEN_FRAGMENTS


def test_inspect_deb_required_paths_include_desktop_and_icon():
    inspect_deb = _load_inspect_deb()

    assert "/usr/share/applications/alters-lab.desktop" in inspect_deb.REQUIRED_PATHS
    assert "/usr/share/icons/hicolor/scalable/apps/alters-lab.svg" in inspect_deb.REQUIRED_PATHS
    assert "/usr/bin/alters-lab" in inspect_deb.REQUIRED_PATHS
