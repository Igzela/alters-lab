"""Tests for P8 Provider Safety Audit tool.

Tests the audit's classification logic, pattern matching, section
audits, and evidence generation without requiring a full repo scan.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest


def _import_audit():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "p8_provider_safety_audit",
        Path(__file__).resolve().parents[3] / "tools" / "p8_provider_safety_audit.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


audit = _import_audit()


def _get_section(report: dict, name: str) -> dict:
    for s in report["sections"]:
        if s["section"] == name:
            return s
    raise KeyError(f"section {name!r} not found")


class TestAuditDefaults:
    def test_json_flag(self):
        args = audit.parse_args(["--json"])
        assert args.json is True

    def test_evidence_path(self):
        args = audit.parse_args(["--evidence", "/tmp/ev.json"])
        assert args.evidence == "/tmp/ev.json"

    def test_repo_root_default(self):
        args = audit.parse_args([])
        assert args.repo_root == "."


class TestClassification:
    def test_source_code_allowed(self):
        assert audit._classify_result("source_code") == "allowed"

    def test_test_allowed(self):
        assert audit._classify_result("test") == "allowed"

    def test_documentation_allowed(self):
        assert audit._classify_result("documentation") == "allowed"

    def test_config_allowed(self):
        assert audit._classify_result("config") == "allowed"

    def test_tool_allowed(self):
        assert audit._classify_result("tool") == "allowed"

    def test_evidence_json_disallowed(self):
        assert audit._classify_result("evidence_json") == "disallowed"

    def test_other_disallowed(self):
        assert audit._classify_result("other") == "disallowed"


class TestFileClassification:
    def test_source_code_path(self, tmp_path):
        path = tmp_path / "src" / "services" / "provider.py"
        assert audit._classify_finding(path, tmp_path) == "source_code"

    def test_test_path(self, tmp_path):
        path = tmp_path / "tests" / "test_provider.py"
        assert audit._classify_finding(path, tmp_path) == "test"

    def test_documentation_path(self, tmp_path):
        path = tmp_path / "README.md"
        assert audit._classify_finding(path, tmp_path) == "documentation"

    def test_evidence_json_path(self, tmp_path):
        harness = tmp_path / "docs" / "harness"
        harness.mkdir(parents=True)
        path = harness / "P8_M5_EVIDENCE.json"
        assert audit._classify_finding(path, tmp_path) == "evidence_json"

    def test_tool_path(self, tmp_path):
        path = tmp_path / "tools" / "smoke.py"
        assert audit._classify_finding(path, tmp_path) == "tool"


class TestScanLogic:
    def test_should_scan_py(self, tmp_path):
        path = tmp_path / "test.py"
        path.touch()
        assert audit._should_scan(path) is True

    def test_should_skip_git(self, tmp_path):
        path = tmp_path / ".git" / "config"
        path.parent.mkdir(parents=True)
        path.touch()
        assert audit._should_scan(path) is False

    def test_should_skip_node_modules(self, tmp_path):
        path = tmp_path / "node_modules" / "pkg" / "index.js"
        path.parent.mkdir(parents=True)
        path.touch()
        assert audit._should_scan(path) is False

    def test_should_skip_non_scan_extension(self, tmp_path):
        path = tmp_path / "image.png"
        path.touch()
        assert audit._should_scan(path) is False


class TestGrepScanSection:
    def test_clean_repo_passes(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "clean.py").write_text("x = 1\n")
        report = audit.scan_repo(tmp_path)
        grep = _get_section(report, "grep_scan")
        assert grep["status"] == "PASS"
        assert grep["disallowed_count"] == 0

    def test_source_finding_allowed(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "provider.py").write_text('ALTERS_PROVIDER_API_KEY = "env"\n')
        report = audit.scan_repo(tmp_path)
        grep = _get_section(report, "grep_scan")
        assert grep["status"] == "PASS"
        assert grep["allowed_count"] > 0
        assert grep["disallowed_count"] == 0

    def test_evidence_finding_disallowed(self, tmp_path):
        harness = tmp_path / "docs" / "harness"
        harness.mkdir(parents=True)
        (harness / "evidence.json").write_text('{"msg": "mock adapter preview test"}\n')
        report = audit.scan_repo(tmp_path)
        grep = _get_section(report, "grep_scan")
        assert grep["status"] == "FAIL"
        assert grep["disallowed_count"] > 0


class TestRouteAuditSection:
    def test_passes_on_real_repo(self):
        report = audit.scan_repo(Path("."))
        route = _get_section(report, "route_audit")
        assert route["status"] == "PASS"
        assert route["missing_routes"] == []


class TestLiveConstantsSection:
    def test_passes_on_real_repo(self):
        report = audit.scan_repo(Path("."))
        lc = _get_section(report, "live_constants")
        assert lc["status"] == "PASS"
        for check in lc["checks"]:
            assert check["status"] == "PASS"


class TestSchemaSafetySection:
    def test_passes_on_real_repo(self):
        report = audit.scan_repo(Path("."))
        schema = _get_section(report, "schema_safety")
        assert schema["status"] == "PASS"


class TestEvidenceContractSection:
    def test_passes_on_real_repo(self):
        report = audit.scan_repo(Path("."))
        ec = _get_section(report, "evidence_contract")
        # Harness docs removed; SKIP is acceptable
        assert ec["status"] in ("PASS", "SKIP")

    def test_fails_on_provider_output(self, tmp_path):
        harness = tmp_path / "docs" / "harness"
        harness.mkdir(parents=True)
        (harness / "P8_M5_E2E_PRODUCT_VALIDATION_EVIDENCE.json").write_text(
            '{"p6_behavior_validated": false, "p6_sealed": false, "msg": "mock adapter preview"}\n'
        )
        report = audit.scan_repo(tmp_path)
        ec = _get_section(report, "evidence_contract")
        assert ec["status"] == "FAIL"

    def test_fails_on_p6_true(self, tmp_path):
        harness = tmp_path / "docs" / "harness"
        harness.mkdir(parents=True)
        (harness / "P8_M5_E2E_PRODUCT_VALIDATION_EVIDENCE.json").write_text(
            '{"p6_behavior_validated": true, "p6_sealed": false}\n'
        )
        report = audit.scan_repo(tmp_path)
        ec = _get_section(report, "evidence_contract")
        assert ec["status"] == "FAIL"


class TestSecretPolicySection:
    def test_passes_on_real_repo(self):
        report = audit.scan_repo(Path("."))
        sp = _get_section(report, "secret_policy")
        assert sp["status"] == "PASS"


class TestMutationBoundarySection:
    def test_passes_on_real_repo(self):
        report = audit.scan_repo(Path("."))
        mb = _get_section(report, "mutation_boundary")
        assert mb["status"] == "PASS"


class TestAuditAssertion:
    def test_assert_passes_on_clean(self):
        report = {"status": "PASS", "p6_behavior_validated": False, "p6_sealed": False}
        audit.assert_audit_passes(report)

    def test_assert_fails_on_status_fail(self):
        report = {"status": "FAIL", "failed_sections": ["grep_scan"], "p6_behavior_validated": False, "p6_sealed": False}
        with pytest.raises(AssertionError):
            audit.assert_audit_passes(report)

    def test_assert_fails_on_p6_true(self):
        report = {"status": "PASS", "p6_behavior_validated": True, "p6_sealed": False}
        with pytest.raises(AssertionError):
            audit.assert_audit_passes(report)


class TestEvidenceContract:
    def test_committed_evidence_has_no_provider_output(self):
        evidence_path = Path(__file__).resolve().parents[3] / "docs" / "harness" / "P8_M5_E2E_PRODUCT_VALIDATION_EVIDENCE.json"
        if not evidence_path.exists():
            pytest.skip("evidence file not present")
        evidence_str = evidence_path.read_text(encoding="utf-8")
        assert "mock adapter preview" not in evidence_str
        assert "mock dialogue preview" not in evidence_str
        assert "mock weekly review assistant" not in evidence_str
        assert "deterministic placeholder" not in evidence_str
