"""Tests for the P7-M8 local app smoke runner."""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SMOKE_SCRIPT = REPO_ROOT / "tools" / "p7_local_app_smoke.py"


def load_smoke_module():
    spec = importlib.util.spec_from_file_location("p7_local_app_smoke", SMOKE_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_args_requires_deb_path():
    module = load_smoke_module()

    args = module.parse_args(["--deb", "dist/deb/alters-lab_0.1.0_amd64.deb", "--json"])

    assert args.deb == "dist/deb/alters-lab_0.1.0_amd64.deb"
    assert args.json is True


def test_choose_port_returns_available_local_port():
    module = load_smoke_module()

    port = module.choose_port()

    assert isinstance(port, int)
    assert 1024 <= port <= 65535


def test_smoke_note_is_synthetic_and_not_p6_evidence():
    module = load_smoke_module()

    assert "Synthetic P7 smoke" in module.SMOKE_NOTE
    assert "outside P6 validation" in module.SMOKE_NOTE
    assert "temporary HOME" in module.SMOKE_NOTE


def test_smoke_script_does_not_call_behavior_validation_or_closeout_endpoints():
    source = SMOKE_SCRIPT.read_text(encoding="utf-8")

    assert "/behavior-validation/evaluate" not in source
    assert "/phase6-closeout" not in source
    assert "P6_BEHAVIOR_VALIDATED" not in source


def test_report_assertions_require_p6_to_remain_unsealed():
    module = load_smoke_module()
    report = {
        "server": {
            "frontend_index_loaded": True,
            "frontend_asset_loaded": True,
        },
        "provider": {
            "test": {
                "network_call_made": False,
                "provider_ready": True,
            },
        },
        "runtime_data": {
            "synthetic_smoke_only": True,
            "record_paths": {
                "weekly_notes": [".local/share/alters-lab/product/weekly_notes/note.yaml"],
                "weekly_reviews": [".local/share/alters-lab/product/weekly_reviews/review.yaml"],
                "calibration_records": [".local/share/alters-lab/product/calibration_records/score.yaml"],
            },
        },
        "backup": {
            "secrets_included": False,
        },
        "p6_behavior_validated": False,
        "p6_sealed": False,
    }

    module._assert_report_passes(report)


def test_report_redaction_removes_temp_root_paths(tmp_path):
    module = load_smoke_module()
    value = {
        "path": str(tmp_path / "home" / ".local" / "share" / "alters-lab"),
        "nested": [str(tmp_path / "pkgroot" / "opt" / "alters-lab")],
    }

    redacted = module._redact_temp_paths(value, tmp_path)

    assert str(tmp_path) not in str(redacted)
    assert "[temp-root]" in redacted["path"]
