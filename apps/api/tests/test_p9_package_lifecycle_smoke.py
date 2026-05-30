"""Tests for P9 disposable dpkg lifecycle smoke script.

Tests the smoke script's safe defaults, redaction, evidence contract,
and assertion logic without performing real dpkg operations.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def _import_smoke():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "p9_package_lifecycle_smoke",
        Path(__file__).resolve().parents[3] / "tools" / "p9_package_lifecycle_smoke.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


smoke = _import_smoke()


def _make_valid_report() -> dict:
    return {
        "install": {
            "dpkg_returncode": 0,
            "dpkg_stderr": "",
            "package_files": {
                "opt_alters_lab_exists": True,
                "usr_bin_launcher": True,
                "web_dist_exists": True,
                "venv_exists": True,
                "desktop_entry": True,
                "icon": True,
            },
            "user_data_before_app_smoke": {
                "config_dir_exists": False,
                "config_file_exists": False,
                "secrets_file_exists": False,
                "data_dir_exists": False,
                "state_dir_exists": False,
                "product_dir_exists": False,
            },
            "post_install_app_smoke": {
                "status": "PASS",
                "routes_checked": [
                    "/local-app/status",
                    "/runtime-layout/status",
                    "/provider-config/status",
                ],
                "local_app_status": {"status": "ok"},
                "runtime_layout_status": {"status": "ok"},
                "provider_config_status": {"status": "ok", "provider_mode": "disabled"},
                "provider_mode": "disabled",
                "behavior_validated": False,
                "p6_sealed": False,
                "real_provider_call_made": False,
            },
        },
        "upgrade": {
            "dpkg_returncode": 0,
            "dpkg_stderr": "",
            "user_data_preserved": {
                "secrets_file_exists": True,
                "config_dir_exists": True,
                "data_dir_exists": True,
            },
            "content_preservation": {
                "config_hash_preserved_after_upgrade": True,
                "secret_hash_preserved_after_upgrade": True,
                "product_record_hash_preserved_after_upgrade": True,
                "secrets_mode_preserved_after_upgrade": True,
            },
        },
        "remove": {
            "dpkg_returncode": 0,
            "dpkg_stderr": "",
            "package_files_after": {
                "opt_alters_lab_exists": False,
                "usr_bin_launcher": False,
                "desktop_entry": False,
                "web_dist_exists": False,
                "venv_exists": False,
                "icon": False,
            },
            "package_owned_payload_removed": True,
            "secrets_preserved": {
                "secrets_file_exists": True,
                "config_dir_exists": True,
                "data_dir_exists": True,
                "product_dir_exists": True,
            },
            "content_preservation": {
                "config_hash_preserved_after_remove": True,
                "secret_hash_preserved_after_remove": True,
                "product_record_hash_preserved_after_remove": True,
                "secrets_mode_preserved_after_remove": True,
            },
        },
        "safety": {
            "behavior_validated": False,
            "p6_sealed": False,
            "no_provider_calls": True,
            "host_mutation_detected": False,
        },
    }


class TestArgParsing:
    def test_deb_required(self):
        with pytest.raises(SystemExit):
            smoke.parse_args([])

    def test_json_flag(self):
        args = smoke.parse_args(["--deb", "/tmp/test.deb", "--json"])
        assert args.json is True

    def test_keep_temp_flag(self):
        args = smoke.parse_args(["--deb", "/tmp/test.deb", "--keep-temp"])
        assert args.keep_temp is True

    def test_evidence_path(self):
        args = smoke.parse_args(["--deb", "/tmp/test.deb", "--evidence", "/tmp/ev.json"])
        assert args.evidence == "/tmp/ev.json"

    def test_defaults(self):
        args = smoke.parse_args(["--deb", "/tmp/test.deb"])
        assert args.json is False
        assert args.keep_temp is False
        assert args.evidence is None


class TestRedaction:
    def test_redact_temp_root_from_strings(self):
        temp = Path("/tmp/alters-lab-p9-smoke-xyz")
        val = f"config at {temp}/home/.config/alters-lab"
        redacted = smoke._redact_temp_paths(val, temp)
        assert str(temp) not in redacted
        assert "[temp-root]" in redacted

    def test_redact_temp_root_from_dicts(self):
        temp = Path("/tmp/alters-lab-p9-smoke-xyz")
        val = {"path": str(temp / "data"), "nested": {"p": str(temp)}}
        redacted = smoke._redact_temp_paths(val, temp)
        assert str(temp) not in json.dumps(redacted)

    def test_redact_temp_root_from_lists(self):
        temp = Path("/tmp/alters-lab-p9-smoke-xyz")
        val = [str(temp / "a"), str(temp / "b")]
        redacted = smoke._redact_temp_paths(val, temp)
        assert all(str(temp) not in r for r in redacted)

    def test_redact_temp_root_preserves_non_matching(self):
        temp = Path("/tmp/alters-lab-p9-smoke-xyz")
        val = {"status": "PASS", "count": 42}
        redacted = smoke._redact_temp_paths(val, temp)
        assert redacted == val

    def test_redact_sensitive_api_key(self):
        data = {"api_key": "sk-secret-123", "mode": "mock"}
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["api_key"] == "[redacted-secret]"
        assert redacted["mode"] == "mock"

    def test_redact_sensitive_key_name(self):
        data = {"key_name": "alters-lab/provider-api-key"}
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["key_name"] == "[redacted-secret]"

    def test_redact_sensitive_output_preview(self):
        data = {"output_preview": "some provider text", "status": "ok"}
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["output_preview"] == "[redacted-provider-output]"
        assert redacted["status"] == "ok"

    def test_redact_sensitive_suggestion(self):
        data = {"suggestion": "some suggestion", "label": "unverified"}
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["suggestion"] == "[redacted-provider-output]"
        assert redacted["label"] == "unverified"

    def test_redact_sensitive_nested(self):
        data = {
            "install": {"api_key": "secret"},
            "provider": {"output_preview": "text"},
        }
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["install"]["api_key"] == "[redacted-secret]"
        assert redacted["provider"]["output_preview"] == "[redacted-provider-output]"

    def test_redact_sensitive_preserves_safety_flags(self):
        data = {
            "behavior_validated": False,
            "p6_sealed": False,
            "no_provider_calls": True,
            "api_key": "secret",
        }
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["behavior_validated"] is False
        assert redacted["p6_sealed"] is False
        assert redacted["no_provider_calls"] is True
        assert redacted["api_key"] == "[redacted-secret]"

    def test_redact_provider_output_patterns(self):
        data = {
            "message": "Mock adapter preview returned. No network call made.",
            "other": "keep this",
        }
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["message"] == "[redacted-provider-output]"
        assert redacted["other"] == "keep this"


class TestReportContract:
    def test_assert_passes_on_valid_report(self):
        smoke._assert_report_passes(_make_valid_report())

    def test_assert_fails_on_install_failure(self):
        report = _make_valid_report()
        report["install"]["dpkg_returncode"] = 1
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_package_creates_user_data(self):
        report = _make_valid_report()
        report["install"]["user_data_before_app_smoke"]["config_file_exists"] = True
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_upgrade_data_loss(self):
        report = _make_valid_report()
        report["upgrade"]["content_preservation"]["config_hash_preserved_after_upgrade"] = False
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_remove_secret_loss(self):
        report = _make_valid_report()
        report["remove"]["content_preservation"]["secret_hash_preserved_after_remove"] = False
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_package_files_not_removed(self):
        report = _make_valid_report()
        report["remove"]["package_files_after"]["web_dist_exists"] = True
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_p6_true(self):
        report = _make_valid_report()
        report["safety"]["behavior_validated"] = True
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_host_mutation(self):
        report = _make_valid_report()
        report["safety"]["host_mutation_detected"] = True
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_provider_calls(self):
        report = _make_valid_report()
        report["safety"]["no_provider_calls"] = False
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_app_smoke_p6_true(self):
        report = _make_valid_report()
        report["install"]["post_install_app_smoke"]["behavior_validated"] = True
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_app_smoke_provider_not_disabled(self):
        report = _make_valid_report()
        report["install"]["post_install_app_smoke"]["provider_mode"] = "mock"
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_app_smoke_missing(self):
        report = _make_valid_report()
        report["install"]["post_install_app_smoke"] = None
        with pytest.raises(AssertionError, match="post_install_app_smoke missing"):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_app_smoke_not_pass(self):
        report = _make_valid_report()
        report["install"]["post_install_app_smoke"]["status"] = "FAIL"
        with pytest.raises(AssertionError, match="app smoke failed"):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_missing_route(self):
        report = _make_valid_report()
        report["install"]["post_install_app_smoke"]["routes_checked"] = ["/local-app/status"]
        with pytest.raises(AssertionError, match="not checked"):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_route_status_not_ok(self):
        report = _make_valid_report()
        report["install"]["post_install_app_smoke"]["local_app_status"]["status"] = "error"
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_passes_with_opt_residual_and_payload_removed(self):
        report = _make_valid_report()
        report["remove"]["package_files_after"]["opt_alters_lab_exists"] = True
        report["remove"]["package_owned_payload_removed"] = True
        smoke._assert_report_passes(report)

    def test_assert_fails_with_opt_residual_and_payload_not_removed(self):
        report = _make_valid_report()
        report["remove"]["package_files_after"]["opt_alters_lab_exists"] = True
        report["remove"]["package_owned_payload_removed"] = False
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_remove_user_data_loss(self):
        report = _make_valid_report()
        report["remove"]["secrets_preserved"]["product_dir_exists"] = False
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)


class TestSafetyFlags:
    def test_smoke_note_is_synthetic(self):
        assert "synthetic" in smoke.SMOKE_NOTE.lower()
        assert "p9" in smoke.SMOKE_NOTE.lower()

    def test_safety_report_fields(self):
        safety = {
            "behavior_validated": False,
            "p6_sealed": False,
            "no_provider_calls": True,
            "host_mutation_detected": False,
            "method_is_extract_only": False,
        }
        assert safety["behavior_validated"] is False
        assert safety["p6_sealed"] is False
        assert safety["no_provider_calls"] is True
        assert safety["host_mutation_detected"] is False
        assert safety["method_is_extract_only"] is False


class TestContentHashing:
    def test_file_hash_deterministic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        h1 = smoke._file_hash(f)
        h2 = smoke._file_hash(f)
        assert h1 == h2
        assert len(h1) == 64  # sha256 hex

    def test_file_hash_changes_on_content_change(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        h1 = smoke._file_hash(f)
        f.write_text("world")
        h2 = smoke._file_hash(f)
        assert h1 != h2

    def test_collect_content_hashes_missing_files(self, tmp_path):
        hashes = smoke._collect_content_hashes(tmp_path)
        assert all(v is None for v in hashes.values())

    def test_collect_content_hashes_existing_files(self, tmp_path):
        config_dir = tmp_path / ".config" / "alters-lab"
        config_dir.mkdir(parents=True)
        (config_dir / "config.yaml").write_text("test")
        (config_dir / "secrets.yaml").write_text("secret")
        hashes = smoke._collect_content_hashes(tmp_path)
        assert hashes["config"] is not None
        assert hashes["secrets"] is not None
        assert hashes["weekly_note"] is None
