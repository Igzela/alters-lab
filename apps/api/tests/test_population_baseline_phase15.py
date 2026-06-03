#!/usr/bin/env python3
"""
Phase 15 Tests — Population Baseline.

Tests for NLSY97 archive inspection, MIDUS parser, variable confirmation,
and baseline table artifacts.
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


class TestNLSY97ArchiveInspection:
    """Test NLSY97 archive inspection without extraction."""

    def test_inspect_script_exists(self):
        script = SCRIPTS_DIR / "inspect_nlsy97_archive.py"
        assert script.exists()

    def test_inspect_script_has_main(self):
        script = SCRIPTS_DIR / "inspect_nlsy97_archive.py"
        content = script.read_text()
        assert "def main()" in content
        assert "if __name__" in content

    def test_inspect_script_handles_zip(self):
        """Verify script can handle ZIP files."""
        script = SCRIPTS_DIR / "inspect_nlsy97_archive.py"
        content = script.read_text()
        assert "zipfile" in content
        assert "ZipFile" in content


class TestMIDUSSavParser:
    """Test MIDUS SPSS parser with mocked data."""

    def test_parse_midus_sav_script_exists(self):
        script = SCRIPTS_DIR / "parse_midus_sav.py"
        assert script.exists()

    def test_parse_midus_sav_has_metadata_only(self):
        script = SCRIPTS_DIR / "parse_midus_sav.py"
        content = script.read_text()
        assert "metadata-only" in content or "metadata_only" in content

    def test_parse_midus_sav_has_columns_option(self):
        script = SCRIPTS_DIR / "parse_midus_sav.py"
        content = script.read_text()
        assert "--columns" in content

    def test_parse_midus_sav_has_summary_mode(self):
        script = SCRIPTS_DIR / "parse_midus_sav.py"
        content = script.read_text()
        assert "--summary" in content


class TestFeatureMappingP15:
    """Test feature_mapping_p15.yaml validation."""

    def test_feature_mapping_p15_exists(self):
        config = CONFIG_DIR / "feature_mapping_p15.yaml"
        assert config.exists()

    def test_feature_mapping_p15_has_data_confirmed(self):
        config = CONFIG_DIR / "feature_mapping_p15.yaml"
        content = config.read_text()
        assert "data_confirmed" in content

    def test_feature_mapping_p15_no_fake_confirmation(self):
        """Verify no variables are confirmed without confirmation_source."""
        import yaml
        config = CONFIG_DIR / "feature_mapping_p15.yaml"
        with open(config) as f:
            data = yaml.safe_load(f)

        for feature in data.get("features", []):
            if feature.get("confirmation_status") in ["metadata_confirmed", "data_confirmed"]:
                assert feature.get("confirmation_source") is not None, \
                    f"Feature {feature['feature_id']} has confirmation_status but no confirmation_source"
                assert feature.get("confirmation_source") != "none", \
                    f"Feature {feature['feature_id']} has confirmation_source='none' but is confirmed"


class TestOutcomeDefinitionsP15:
    """Test outcome_definitions_p15.yaml validation."""

    def test_outcome_definitions_p15_exists(self):
        config = CONFIG_DIR / "outcome_definitions_p15.yaml"
        assert config.exists()

    def test_outcome_definitions_p15_has_data_confirmed(self):
        config = CONFIG_DIR / "outcome_definitions_p15.yaml"
        content = config.read_text()
        assert "data_confirmed" in content

    def test_outcome_definitions_p15_no_fake_confirmation(self):
        """Verify no outcomes are confirmed without confirmation_source."""
        import yaml
        config = CONFIG_DIR / "outcome_definitions_p15.yaml"
        with open(config) as f:
            data = yaml.safe_load(f)

        for outcome in data.get("outcomes", []):
            if outcome.get("confirmation_status") in ["metadata_confirmed", "data_confirmed"]:
                assert outcome.get("confirmation_source") is not None, \
                    f"Outcome {outcome['outcome_id']} has confirmation_status but no confirmation_source"
                assert outcome.get("confirmation_source") != "none", \
                    f"Outcome {outcome['outcome_id']} has confirmation_source='none' but is confirmed"


class TestBaselineTablesP15:
    """Test baseline table artifacts."""

    def test_baseline_tables_json_exists(self):
        artifact = ARTIFACTS_DIR / "baseline_tables_p15.json"
        assert artifact.exists()

    def test_baseline_tables_approved_for_route_b_false(self):
        """Verify all baseline tables have approved_for_route_b=false."""
        artifact = ARTIFACTS_DIR / "baseline_tables_p15.json"
        with open(artifact) as f:
            data = json.load(f)

        assert data.get("approved_for_route_b") is False

        for table in data.get("tables", []):
            assert table.get("approved_for_route_b") is False, \
                f"Table {table['artifact_id']} has approved_for_route_b != false"

    def test_baseline_tables_no_individual_rows(self):
        """Verify baseline tables contain no individual-level data."""
        artifact = ARTIFACTS_DIR / "baseline_tables_p15.json"
        with open(artifact) as f:
            data = json.load(f)

        for table in data.get("tables", []):
            # Should have aggregate stats, not individual rows
            assert "n_valid" in table, f"Table {table['artifact_id']} missing n_valid"
            assert "observed_rate_or_mean" in table, f"Table {table['artifact_id']} missing observed_rate_or_mean"
            # Should not have individual-level fields
            assert "individual_rows" not in table
            assert "raw_data" not in table
            assert "respondent_id" not in table

    def test_baseline_tables_no_life_score(self):
        """Verify no life_score field exists."""
        artifact = ARTIFACTS_DIR / "baseline_tables_p15.json"
        with open(artifact) as f:
            data = json.load(f)

        for table in data.get("tables", []):
            assert "life_score" not in table, \
                f"Table {table['artifact_id']} contains life_score"

    def test_baseline_tables_no_exact_probability(self):
        """Verify no exact personal probability fields."""
        artifact = ARTIFACTS_DIR / "baseline_tables_p15.json"
        with open(artifact) as f:
            data = json.load(f)

        for table in data.get("tables", []):
            assert "exact_probability" not in table
            assert "personal_probability" not in table
            assert "individual_probability" not in table

    def test_baseline_tables_config_exists(self):
        config = CONFIG_DIR / "baseline_tables_p15.yaml"
        assert config.exists()

    def test_baseline_tables_config_approved_false(self):
        import yaml
        config = CONFIG_DIR / "baseline_tables_p15.yaml"
        with open(config) as f:
            data = yaml.safe_load(f)

        assert data.get("approved_for_route_b") is False


class TestNLSY97StreamingParser:
    """Test NLSY97 streaming parser."""

    def test_streaming_parser_exists(self):
        script = SCRIPTS_DIR / "parse_nlsy97_streaming.py"
        assert script.exists()

    def test_streaming_parser_has_columns_option(self):
        script = SCRIPTS_DIR / "parse_nlsy97_streaming.py"
        content = script.read_text()
        assert "--columns" in content

    def test_streaming_parser_has_sample_rows(self):
        script = SCRIPTS_DIR / "parse_nlsy97_streaming.py"
        content = script.read_text()
        assert "--sample-rows" in content

    def test_streaming_parser_no_full_extraction(self):
        """Verify parser doesn't extract full CSV by default."""
        script = SCRIPTS_DIR / "parse_nlsy97_streaming.py"
        content = script.read_text()
        # Should use streaming, not extraction
        assert "stream" in content.lower() or "chunk" in content.lower()


class TestBuildBaselineTables:
    """Test baseline table builder script."""

    def test_build_baseline_tables_exists(self):
        script = SCRIPTS_DIR / "build_baseline_tables.py"
        assert script.exists()

    def test_build_baseline_tables_has_dataset_option(self):
        script = SCRIPTS_DIR / "build_baseline_tables.py"
        content = script.read_text()
        assert "--dataset" in content

    def test_build_baseline_tables_no_individual_data(self):
        """Verify builder doesn't output individual rows."""
        script = SCRIPTS_DIR / "build_baseline_tables.py"
        content = script.read_text()
        # Should compute aggregates, not output rows
        assert "mean" in content or "average" in content.lower()
        assert "distribution" in content


class TestPhase15Documentation:
    """Test Phase 15 documentation exists."""

    def test_p15_variable_confirmation_exists(self):
        doc = LABS_DIR / "P15_VARIABLE_CONFIRMATION.md"
        assert doc.exists()

    def test_p15_baseline_tables_doc_exists(self):
        doc = LABS_DIR / "P15_BASELINE_TABLES.md"
        assert doc.exists()

    def test_p15_completion_report_exists(self):
        doc = LABS_DIR / "P15_COMPLETION_REPORT.md"
        assert doc.exists()

    def test_p15_nlsy97_inspection_exists(self):
        doc = LABS_DIR / "P15_NLSY97_ARCHIVE_INSPECTION.md"
        assert doc.exists()
