#!/usr/bin/env python3
"""
Phase 16 Tests — Population Baseline.

Tests for NLSY97 variable dictionary, priority search, column verification,
baseline tables, MIDUS cross-wave analysis, and missingness audit.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
LABS_DIR = REPO_ROOT / "labs" / "population_baseline"
SCRIPTS_DIR = LABS_DIR / "scripts"
CONFIG_DIR = LABS_DIR / "config"
ARTIFACTS_DIR = LABS_DIR / "artifacts"


class TestNLSY97VariableDictionary:
    """Test NLSY97 variable dictionary extraction."""

    def test_extract_script_exists(self):
        script = SCRIPTS_DIR / "extract_nlsy97_variable_dictionary.py"
        assert script.exists()

    def test_extract_script_handles_zip(self):
        script = SCRIPTS_DIR / "extract_nlsy97_variable_dictionary.py"
        content = script.read_text()
        assert "zipfile" in content
        assert "ZipFile" in content

    def test_dictionary_yaml_exists(self):
        config = CONFIG_DIR / "nlsy97_variable_dictionary_p16.yaml"
        assert config.exists()

    def test_dictionary_has_variables(self):
        import yaml
        config = CONFIG_DIR / "nlsy97_variable_dictionary_p16.yaml"
        with open(config) as f:
            data = yaml.safe_load(f)
        assert "variables" in data
        assert len(data["variables"]) > 0


class TestNLSY97PrioritySearch:
    """Test NLSY97 priority variable search."""

    def test_search_script_exists(self):
        script = SCRIPTS_DIR / "search_nlsy97_variables.py"
        assert script.exists()

    def test_priority_variables_yaml_exists(self):
        config = CONFIG_DIR / "nlsy97_priority_variables_p16.yaml"
        assert config.exists()

    def test_priority_variables_have_domains(self):
        import yaml
        config = CONFIG_DIR / "nlsy97_priority_variables_p16.yaml"
        with open(config) as f:
            data = yaml.safe_load(f)
        assert "priority_variables" in data
        for var in data["priority_variables"]:
            assert "domain" in var
            assert "confidence" in var


class TestColumnVerification:
    """Test column verification against CSV header."""

    def test_streaming_parser_has_verify_option(self):
        script = SCRIPTS_DIR / "parse_nlsy97_streaming.py"
        content = script.read_text()
        assert "--verify-columns" in content

    def test_verification_artifact_exists(self):
        artifact = ARTIFACTS_DIR / "nlsy97_column_verification_p16.json"
        assert artifact.exists()

    def test_verification_artifact_structure(self):
        artifact = ARTIFACTS_DIR / "nlsy97_column_verification_p16.json"
        with open(artifact) as f:
            data = json.load(f)
        assert "total_candidates" in data
        assert "verified" in data
        assert "not_found" in data


class TestFeatureMappingP16:
    """Test feature_mapping_p16.yaml validation."""

    def test_feature_mapping_p16_exists(self):
        config = CONFIG_DIR / "feature_mapping_p16.yaml"
        assert config.exists()

    def test_feature_mapping_p16_has_data_confirmed(self):
        config = CONFIG_DIR / "feature_mapping_p16.yaml"
        content = config.read_text()
        assert "data_confirmed" in content

    def test_feature_mapping_p16_no_fake_confirmation(self):
        """Verify no variables are confirmed without confirmation_source."""
        import yaml
        config = CONFIG_DIR / "feature_mapping_p16.yaml"
        with open(config) as f:
            data = yaml.safe_load(f)

        for feature in data.get("features", []):
            if feature.get("confirmation_status") in ["metadata_confirmed", "data_confirmed"]:
                assert feature.get("confirmation_source") is not None, \
                    f"Feature {feature['feature_id']} has confirmation_status but no confirmation_source"
                assert feature.get("confirmation_source") != "none", \
                    f"Feature {feature['feature_id']} has confirmation_source='none' but is confirmed"


class TestOutcomeDefinitionsP16:
    """Test outcome_definitions_p16.yaml validation."""

    def test_outcome_definitions_p16_exists(self):
        config = CONFIG_DIR / "outcome_definitions_p16.yaml"
        assert config.exists()

    def test_outcome_definitions_p16_has_data_confirmed(self):
        config = CONFIG_DIR / "outcome_definitions_p16.yaml"
        content = config.read_text()
        assert "data_confirmed" in content


class TestNLSY97BaselineTables:
    """Test NLSY97 baseline table artifacts."""

    def test_baseline_tables_json_exists(self):
        artifact = ARTIFACTS_DIR / "nlsy97_baseline_tables_p16.json"
        assert artifact.exists()

    def test_baseline_tables_approved_for_route_b_false(self):
        """Verify all baseline tables have approved_for_route_b=false."""
        artifact = ARTIFACTS_DIR / "nlsy97_baseline_tables_p16.json"
        with open(artifact) as f:
            data = json.load(f)

        assert data.get("approved_for_route_b") is False

        for table in data.get("tables", []):
            assert table.get("approved_for_route_b") is False, \
                f"Table {table['artifact_id']} has approved_for_route_b != false"

    def test_baseline_tables_no_individual_rows(self):
        """Verify baseline tables contain no individual-level data."""
        artifact = ARTIFACTS_DIR / "nlsy97_baseline_tables_p16.json"
        with open(artifact) as f:
            data = json.load(f)

        for table in data.get("tables", []):
            # Should have aggregate stats, not individual rows
            assert "n_valid" in table, f"Table {table['artifact_id']} missing n_valid"
            assert "missingness_rate" in table, f"Table {table['artifact_id']} missing missingness_rate"
            # Should not have individual-level fields
            assert "individual_rows" not in table
            assert "raw_data" not in table
            assert "respondent_id" not in table

    def test_baseline_tables_no_life_score(self):
        """Verify no life_score field exists."""
        artifact = ARTIFACTS_DIR / "nlsy97_baseline_tables_p16.json"
        with open(artifact) as f:
            data = json.load(f)

        for table in data.get("tables", []):
            assert "life_score" not in table, \
                f"Table {table['artifact_id']} contains life_score"

    def test_baseline_tables_no_exact_probability(self):
        """Verify no exact personal probability fields."""
        artifact = ARTIFACTS_DIR / "nlsy97_baseline_tables_p16.json"
        with open(artifact) as f:
            data = json.load(f)

        for table in data.get("tables", []):
            assert "exact_probability" not in table
            assert "personal_probability" not in table
            assert "individual_probability" not in table


class TestMIDUSCrossWaveAnalysis:
    """Test MIDUS cross-wave analysis outputs."""

    def test_cross_wave_artifact_exists(self):
        artifact = ARTIFACTS_DIR / "midus_cross_wave_analysis_p16.json"
        assert artifact.exists()

    def test_cross_wave_artifact_is_aggregate(self):
        """Verify cross-wave analysis is aggregate-only."""
        artifact = ARTIFACTS_DIR / "midus_cross_wave_analysis_p16.json"
        with open(artifact) as f:
            data = json.load(f)

        assert "waves" in data
        for wave in data["waves"]:
            assert "variables" in wave
            for var_id, var_stats in wave["variables"].items():
                # Should have aggregate stats
                assert "n_valid" in var_stats
                assert "mean" in var_stats
                # Should not have individual-level data
                assert "individual" not in var_stats
                assert "rows" not in var_stats

    def test_cross_wave_no_life_score(self):
        """Verify no life_score field exists."""
        artifact = ARTIFACTS_DIR / "midus_cross_wave_analysis_p16.json"
        with open(artifact) as f:
            data = json.load(f)

        for wave in data.get("waves", []):
            for var_id, var_stats in wave.get("variables", {}).items():
                assert "life_score" not in var_stats

    def test_cross_wave_no_exact_probability(self):
        """Verify no exact personal probability fields."""
        artifact = ARTIFACTS_DIR / "midus_cross_wave_analysis_p16.json"
        with open(artifact) as f:
            data = json.load(f)

        for wave in data.get("waves", []):
            for var_id, var_stats in wave.get("variables", {}).items():
                assert "exact_probability" not in var_stats
                assert "personal_probability" not in var_stats


class TestMissingnessAudit:
    """Test missingness audit outputs."""

    def test_missingness_audit_exists(self):
        artifact = ARTIFACTS_DIR / "missingness_audit_p16.json"
        assert artifact.exists()

    def test_missingness_audit_is_aggregate(self):
        """Verify missingness audit is aggregate-only."""
        artifact = ARTIFACTS_DIR / "missingness_audit_p16.json"
        with open(artifact) as f:
            data = json.load(f)

        assert "midus_audit" in data
        for record in data["midus_audit"]:
            # Should have aggregate stats
            assert "n_total" in record
            assert "n_valid" in record
            assert "n_missing" in record
            assert "missingness_rate" in record
            # Should not have individual-level data
            assert "individual" not in record
            assert "rows" not in record


class TestPhase16Documentation:
    """Test Phase 16 documentation exists."""

    def test_p16_nlsy97_variable_dictionary_exists(self):
        doc = LABS_DIR / "P16_NLSY97_VARIABLE_DICTIONARY.md"
        assert doc.exists()

    def test_p16_nlsy97_priority_variables_exists(self):
        doc = LABS_DIR / "P16_NLSY97_PRIORITY_VARIABLES.md"
        assert doc.exists()

    def test_p16_nlsy97_column_verification_exists(self):
        doc = LABS_DIR / "P16_NLSY97_COLUMN_VERIFICATION.md"
        assert doc.exists()

    def test_p16_variable_confirmation_exists(self):
        doc = LABS_DIR / "P16_VARIABLE_CONFIRMATION.md"
        assert doc.exists()

    def test_p16_nlsy97_baseline_tables_exists(self):
        doc = LABS_DIR / "P16_NLSY97_BASELINE_TABLES.md"
        assert doc.exists()

    def test_p16_midus_cross_wave_exists(self):
        doc = LABS_DIR / "P16_MIDUS_CROSS_WAVE_ANALYSIS.md"
        assert doc.exists()

    def test_p16_missingness_audit_exists(self):
        doc = LABS_DIR / "P16_MISSINGNESS_AUDIT.md"
        assert doc.exists()

    def test_p16_route_b_readiness_exists(self):
        doc = LABS_DIR / "P16_ROUTE_B_READINESS_REVIEW.md"
        assert doc.exists()


class TestPhase16Configs:
    """Test Phase 16 configuration files."""

    def test_nlsy97_baseline_tables_config_exists(self):
        config = CONFIG_DIR / "nlsy97_baseline_tables_p16.yaml"
        assert config.exists()

    def test_midus_cross_wave_config_exists(self):
        config = CONFIG_DIR / "midus_cross_wave_tables_p16.yaml"
        assert config.exists()

    def test_nlsy97_baseline_tables_config_approved_false(self):
        import yaml
        config = CONFIG_DIR / "nlsy97_baseline_tables_p16.yaml"
        with open(config) as f:
            data = yaml.safe_load(f)
        assert data.get("approved_for_route_b") is False

    def test_midus_cross_wave_config_approved_false(self):
        import yaml
        config = CONFIG_DIR / "midus_cross_wave_tables_p16.yaml"
        with open(config) as f:
            data = yaml.safe_load(f)
        assert data.get("approved_for_route_b") is False
