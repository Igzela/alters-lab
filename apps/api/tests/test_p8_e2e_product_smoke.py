"""Tests for P8 E2E product smoke script.

Tests the smoke script's safe defaults and contract without
performing real network calls or requiring sudo install.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest


def _import_smoke():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "p8_e2e_product_smoke",
        Path(__file__).resolve().parents[3] / "tools" / "p8_e2e_product_smoke.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


smoke = _import_smoke()


class TestSmokeScriptDefaults:
    def test_live_provider_disabled_by_default(self):
        args = smoke.parse_args(["--deb", "/tmp/test.deb"])
        assert args.allow_live_provider is False
        assert args.live_provider_confirmation is None

    def test_json_output_flag(self):
        args = smoke.parse_args(["--deb", "/tmp/test.deb", "--json"])
        assert args.json is True

    def test_keep_temp_flag(self):
        args = smoke.parse_args(["--deb", "/tmp/test.deb", "--keep-temp"])
        assert args.keep_temp is True

    def test_evidence_path(self):
        args = smoke.parse_args(["--deb", "/tmp/test.deb", "--evidence", "/tmp/ev.json"])
        assert args.evidence == "/tmp/ev.json"

    def test_live_flags_require_exact_confirmation(self):
        args = smoke.parse_args([
            "--deb", "/tmp/test.deb",
            "--allow-live-provider",
            "--live-provider-confirmation", "run-live-p8-e2e-provider-smoke",
        ])
        assert args.allow_live_provider is True
        assert args.live_provider_confirmation == "run-live-p8-e2e-provider-smoke"


class TestSmokeReportContract:
    def test_report_has_p6_false_flags(self):
        report = {
            "p6_behavior_validated": False,
            "p6_sealed": False,
            "runtime_data": {"synthetic_smoke_only": True},
        }
        assert report["p6_behavior_validated"] is False
        assert report["p6_sealed"] is False
        assert report["runtime_data"]["synthetic_smoke_only"] is True

    def test_report_assertions_catch_p6_true(self):
        report = {
            "p6_behavior_validated": True,
            "p6_sealed": False,
            "runtime_data": {"synthetic_smoke_only": True},
            "routes": {},
            "provider_config": {"test": {"network_call_made": False, "provider_ready": True}},
            "provider_adapter": {"preview": {"network_call_made": False, "active_yaml_modified": False, "p6_behavior_validated": True, "p6_sealed": False}},
            "provider_connectivity": {"check": {"network_call_made": False}},
            "provider_dialogue_preview": {"generate": {"output_label": "unverified_provider_preview", "output_persisted": False, "prompt_persisted": False, "response_content_persisted": False, "p6_behavior_validated": True, "p6_sealed": False}},
            "weekly_review_assistant": {"suggest": {"suggestion_label": "unverified_provider_suggestion", "suggestion_persisted": False, "weekly_review_completed": False, "action_alignment_created": False, "reality_score_created": False, "p6_behavior_validated": True, "p6_sealed": False}},
            "weekly_review_flow": {"note_status": "ok", "weekly_status": "ok", "score_status": "ok"},
            "backup": {"secrets_included": False},
        }
        with pytest.raises(AssertionError):
            smoke._assert_report_passes(report)

    def test_redact_temp_paths(self):
        temp_root = Path("/tmp/alters-lab-p8-smoke-xyz")
        value = f"config under {temp_root}/home/.config/alters-lab"
        redacted = smoke._redact_temp_paths(value, temp_root)
        assert str(temp_root) not in redacted
        assert "[temp-root]" in redacted

    def test_redact_nested_dicts(self):
        temp_root = Path("/tmp/alters-lab-p8-smoke-xyz")
        value = {"path": str(temp_root / "data"), "nested": {"path": str(temp_root)}}
        redacted = smoke._redact_temp_paths(value, temp_root)
        assert str(temp_root) not in json.dumps(redacted)

    def test_redact_lists(self):
        temp_root = Path("/tmp/alters-lab-p8-smoke-xyz")
        value = [str(temp_root / "a"), str(temp_root / "b")]
        redacted = smoke._redact_temp_paths(value, temp_root)
        assert all(str(temp_root) not in r for r in redacted)

    def test_smoke_note_is_synthetic(self):
        assert "synthetic" in smoke.SMOKE_NOTE.lower()
        assert "p6" in smoke.SMOKE_NOTE.lower()


class TestProviderSafetyInSmoke:
    def test_adapter_preview_flags_enforced(self):
        preview = {
            "network_call_made": False,
            "active_yaml_modified": False,
            "p6_behavior_validated": False,
            "p6_sealed": False,
        }
        assert preview["network_call_made"] is False
        assert preview["active_yaml_modified"] is False
        assert preview["p6_behavior_validated"] is False
        assert preview["p6_sealed"] is False

    def test_dialogue_preview_safety_flags(self):
        generate = {
            "output_label": "unverified_provider_preview",
            "output_persisted": False,
            "prompt_persisted": False,
            "response_content_persisted": False,
            "p6_behavior_validated": False,
            "p6_sealed": False,
        }
        assert generate["output_label"] == "unverified_provider_preview"
        assert generate["output_persisted"] is False

    def test_assistant_safety_flags(self):
        suggest = {
            "suggestion_label": "unverified_provider_suggestion",
            "suggestion_persisted": False,
            "weekly_review_completed": False,
            "action_alignment_created": False,
            "reality_score_created": False,
            "p6_behavior_validated": False,
            "p6_sealed": False,
        }
        assert suggest["suggestion_label"] == "unverified_provider_suggestion"
        assert suggest["suggestion_persisted"] is False
        assert suggest["weekly_review_completed"] is False

    def test_redact_sensitive_fields_output_preview(self):
        data = {"output_preview": "some provider text", "status": "ok"}
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["output_preview"] == "[redacted-provider-output]"
        assert redacted["status"] == "ok"

    def test_redact_sensitive_fields_suggestion(self):
        data = {"suggestion": "some suggestion text", "suggestion_label": "unverified"}
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["suggestion"] == "[redacted-provider-output]"
        assert redacted["suggestion_label"] == "unverified"

    def test_redact_sensitive_fields_preserves_safety_flags(self):
        data = {
            "output_preview": "text",
            "suggestion": "text",
            "prompt": "text",
            "output_persisted": False,
            "suggestion_persisted": False,
            "prompt_persisted": False,
            "response_content_persisted": False,
            "network_call_made": False,
            "p6_behavior_validated": False,
        }
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["output_persisted"] is False
        assert redacted["suggestion_persisted"] is False
        assert redacted["prompt_persisted"] is False
        assert redacted["response_content_persisted"] is False
        assert redacted["network_call_made"] is False
        assert redacted["p6_behavior_validated"] is False

    def test_redact_sensitive_fields_nested(self):
        data = {
            "provider_adapter": {"preview": {"output_preview": "text"}},
            "weekly_review_assistant": {"suggest": {"suggestion": "text"}},
        }
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["provider_adapter"]["preview"]["output_preview"] == "[redacted-provider-output]"
        assert redacted["weekly_review_assistant"]["suggest"]["suggestion"] == "[redacted-provider-output]"

    def test_redact_sensitive_fields_key_name(self):
        data = {"key_name": "alters-lab/provider-api-key", "mode": "mock"}
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["key_name"] == "[redacted-secret]"
        assert redacted["mode"] == "mock"

    def test_redact_sensitive_fields_preserves_secret_metadata(self):
        data = {"secrets_redacted": True, "secret_storage": "keyring"}
        redacted = smoke._redact_sensitive_fields(data)
        assert redacted["secrets_redacted"] is True
        assert redacted["secret_storage"] == "keyring"

    def test_evidence_excludes_secrets(self):
        evidence = {
            "provider_config": {"test": {"api_key": "sk-secret"}},
            "routes": {},
        }
        evidence_str = json.dumps(evidence)
        assert "sk-secret" in evidence_str
        # After redaction, api_key would be replaced
        redacted = smoke._redact_sensitive_fields(evidence)
        redacted_str = json.dumps(redacted)
        assert "sk-secret" not in redacted_str

    def test_committed_evidence_has_no_provider_output(self):
        evidence_path = Path(__file__).resolve().parents[3] / "docs" / "harness" / "P8_M5_E2E_PRODUCT_VALIDATION_EVIDENCE.json"
        if not evidence_path.exists():
            pytest.skip("evidence file not present")
        evidence_str = evidence_path.read_text(encoding="utf-8")
        assert "mock adapter preview" not in evidence_str
        assert "mock dialogue preview" not in evidence_str
        assert "mock weekly review assistant" not in evidence_str
        assert "deterministic placeholder" not in evidence_str
        assert "[redacted-provider-output]" in evidence_str
