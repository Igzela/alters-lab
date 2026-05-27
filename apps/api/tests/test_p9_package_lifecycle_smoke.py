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
            "p6_behavior_validated": False,
            "p6_sealed": False,
            "no_provider_calls": True,
            "api_key": "secret",
        }
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["p6_behavior_validated"] is False
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
        report = {
            "install": {
                "dpkg_returncode": 0,
                "package_files": {
                    "opt_alters_lab_exists": True,
                    "usr_bin_launcher": True,
                },
            },
            "upgrade": {
                "dpkg_returncode": 0,
                "user_data_preserved": {
                    "secrets_file_exists": True,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                },
            },
            "remove": {
                "dpkg_returncode": 0,
                "secrets_preserved": {
                    "secrets_file_exists": True,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                    "product_dir_exists": True,
                },
            },
            "safety": {
                "p6_behavior_validated": False,
                "p6_sealed": False,
                "no_provider_calls": True,
                "host_mutation_detected": False,
            },
        }
        smoke._assert_report_passes(report)

    def test_assert_fails_on_install_failure(self):
        report = {
            "install": {
                "dpkg_returncode": 1,
                "dpkg_stderr": "dpkg: error processing archive",
                "package_files": {
                    "opt_alters_lab_exists": False,
                    "usr_bin_launcher": False,
                },
            },
            "upgrade": {
                "dpkg_returncode": 0,
                "user_data_preserved": {
                    "secrets_file_exists": True,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                },
            },
            "remove": {
                "dpkg_returncode": 0,
                "secrets_preserved": {
                    "secrets_file_exists": True,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                    "product_dir_exists": True,
                },
            },
            "safety": {
                "p6_behavior_validated": False,
                "p6_sealed": False,
                "no_provider_calls": True,
                "host_mutation_detected": False,
            },
        }
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_upgrade_data_loss(self):
        report = {
            "install": {
                "dpkg_returncode": 0,
                "package_files": {
                    "opt_alters_lab_exists": True,
                    "usr_bin_launcher": True,
                },
            },
            "upgrade": {
                "dpkg_returncode": 0,
                "user_data_preserved": {
                    "secrets_file_exists": False,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                },
            },
            "remove": {
                "dpkg_returncode": 0,
                "secrets_preserved": {
                    "secrets_file_exists": True,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                    "product_dir_exists": True,
                },
            },
            "safety": {
                "p6_behavior_validated": False,
                "p6_sealed": False,
                "no_provider_calls": True,
                "host_mutation_detected": False,
            },
        }
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_remove_secret_loss(self):
        report = {
            "install": {
                "dpkg_returncode": 0,
                "package_files": {
                    "opt_alters_lab_exists": True,
                    "usr_bin_launcher": True,
                },
            },
            "upgrade": {
                "dpkg_returncode": 0,
                "user_data_preserved": {
                    "secrets_file_exists": True,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                },
            },
            "remove": {
                "dpkg_returncode": 0,
                "secrets_preserved": {
                    "secrets_file_exists": False,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                    "product_dir_exists": True,
                },
            },
            "safety": {
                "p6_behavior_validated": False,
                "p6_sealed": False,
                "no_provider_calls": True,
                "host_mutation_detected": False,
            },
        }
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_p6_true(self):
        report = {
            "install": {
                "dpkg_returncode": 0,
                "package_files": {
                    "opt_alters_lab_exists": True,
                    "usr_bin_launcher": True,
                },
            },
            "upgrade": {
                "dpkg_returncode": 0,
                "user_data_preserved": {
                    "secrets_file_exists": True,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                },
            },
            "remove": {
                "dpkg_returncode": 0,
                "secrets_preserved": {
                    "secrets_file_exists": True,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                    "product_dir_exists": True,
                },
            },
            "safety": {
                "p6_behavior_validated": True,
                "p6_sealed": False,
                "no_provider_calls": True,
                "host_mutation_detected": False,
            },
        }
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_host_mutation(self):
        report = {
            "install": {
                "dpkg_returncode": 0,
                "package_files": {
                    "opt_alters_lab_exists": True,
                    "usr_bin_launcher": True,
                },
            },
            "upgrade": {
                "dpkg_returncode": 0,
                "user_data_preserved": {
                    "secrets_file_exists": True,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                },
            },
            "remove": {
                "dpkg_returncode": 0,
                "secrets_preserved": {
                    "secrets_file_exists": True,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                    "product_dir_exists": True,
                },
            },
            "safety": {
                "p6_behavior_validated": False,
                "p6_sealed": False,
                "no_provider_calls": True,
                "host_mutation_detected": True,
            },
        }
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_assert_fails_on_provider_calls(self):
        report = {
            "install": {
                "dpkg_returncode": 0,
                "package_files": {
                    "opt_alters_lab_exists": True,
                    "usr_bin_launcher": True,
                },
            },
            "upgrade": {
                "dpkg_returncode": 0,
                "user_data_preserved": {
                    "secrets_file_exists": True,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                },
            },
            "remove": {
                "dpkg_returncode": 0,
                "secrets_preserved": {
                    "secrets_file_exists": True,
                    "config_dir_exists": True,
                    "data_dir_exists": True,
                    "product_dir_exists": True,
                },
            },
            "safety": {
                "p6_behavior_validated": False,
                "p6_sealed": False,
                "no_provider_calls": False,
                "host_mutation_detected": False,
            },
        }
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)


class TestSafetyFlags:
    def test_smoke_note_is_synthetic(self):
        assert "synthetic" in smoke.SMOKE_NOTE.lower()
        assert "p9" in smoke.SMOKE_NOTE.lower()
        assert "not p6" in smoke.SMOKE_NOTE.lower() or "p6 evidence" in smoke.SMOKE_NOTE.lower()

    def test_safety_report_fields(self):
        safety = {
            "p6_behavior_validated": False,
            "p6_sealed": False,
            "no_provider_calls": True,
            "host_mutation_detected": False,
            "method_is_extract_only": False,
        }
        assert safety["p6_behavior_validated"] is False
        assert safety["p6_sealed"] is False
        assert safety["no_provider_calls"] is True
        assert safety["host_mutation_detected"] is False
        assert safety["method_is_extract_only"] is False
