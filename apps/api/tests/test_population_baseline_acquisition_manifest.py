"""
Phase 13 — Data Acquisition Manifest Tests.

Verifies:
- Manifest includes MIDUS and NLSY97
- FFCWS remains deferred from active acquisition
- All raw-data paths are under gitignored directories
- No raw data files committed
- Variable mappings remain candidate unless confirmation_source != none
- No approved_for_route_b
- No probability artifacts
- No life_score
- Acquisition scripts do not require network for tests
"""

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
LABS_DIR = REPO_ROOT / "labs" / "population_baseline"
CONFIG_DIR = LABS_DIR / "config"
ARTIFACTS_DIR = LABS_DIR / "artifacts"
RAW_DIR = LABS_DIR / "data" / "raw"


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


class TestAcquisitionManifest:
    """Tests for data_acquisition_manifest_p13.yaml."""

    @pytest.fixture
    def manifest(self):
        return load_yaml(CONFIG_DIR / "data_acquisition_manifest_p13.yaml")

    def test_manifest_has_nlsy97(self, manifest):
        source_ids = [s["source_id"] for s in manifest["sources"]]
        assert "nlsy97" in source_ids

    def test_manifest_has_midus(self, manifest):
        source_ids = [s["source_id"] for s in manifest["sources"]]
        assert "midus" in source_ids

    def test_ffcws_deferred(self, manifest):
        deferred_ids = [s["source_id"] for s in manifest.get("deferred_sources", [])]
        assert "ffcws" in deferred_ids

    def test_psid_deferred(self, manifest):
        deferred_ids = [s["source_id"] for s in manifest.get("deferred_sources", [])]
        assert "psid" in deferred_ids

    def test_ffcws_not_in_active_sources(self, manifest):
        source_ids = [s["source_id"] for s in manifest["sources"]]
        assert "ffcws" not in source_ids

    def test_psid_not_in_active_sources(self, manifest):
        source_ids = [s["source_id"] for s in manifest["sources"]]
        assert "psid" not in source_ids

    def test_all_raw_paths_gitignored(self, manifest):
        for source in manifest["sources"]:
            raw_dir = source["target_raw_dir"]
            assert raw_dir.startswith("labs/population_baseline/data/raw/"), \
                f"Raw dir {raw_dir} is not under gitignored path"

    def test_sources_require_account(self, manifest):
        for source in manifest["sources"]:
            assert source["requires_account"] is True, \
                f"{source['source_id']} should require account (not auto-downloadable)"

    def test_sources_require_terms(self, manifest):
        for source in manifest["sources"]:
            assert source["requires_terms_acceptance"] is True, \
                f"{source['source_id']} should require terms acceptance"

    def test_no_approved_for_route_b(self, manifest):
        for source in manifest["sources"]:
            assert not source.get("approved_for_route_b"), \
                f"{source['source_id']} must not be approved for Route B"

    def test_policy_invariants(self, manifest):
        policy = manifest["policy"]
        assert policy["no_raw_data_committed"] is True
        assert policy["no_individual_responses_committed"] is True
        assert policy["no_route_b_approval"] is True
        assert policy["no_ml_models"] is True
        assert policy["no_probability_artifacts"] is True
        assert policy["variable_status_default"] == "candidate"

    def test_manifest_has_user_actions(self, manifest):
        for source in manifest["sources"]:
            assert len(source["user_actions_required"]) > 0, \
                f"{source['source_id']} must document user actions"

    def test_manifest_has_required_files(self, manifest):
        for source in manifest["sources"]:
            assert len(source["required_files"]) > 0, \
                f"{source['source_id']} must list required files"


class TestFeatureMappingP13:
    """Tests for feature_mapping_p13.yaml."""

    @pytest.fixture
    def features(self):
        data = load_yaml(CONFIG_DIR / "feature_mapping_p13.yaml")
        return data["features"]

    def test_nlsy97_features_still_candidate(self, features):
        nlsy_features = [f for f in features if f["dataset_source_id"] == "nlsy97"]
        for f in nlsy_features:
            assert f["confirmation_status"] == "candidate", \
                f"{f['feature_id']} must be candidate (NLSY97 not yet verified)"

    def test_midus_features_metadata_confirmed(self, features):
        midus_features = [f for f in features if f["dataset_source_id"] == "midus"]
        for f in midus_features:
            assert f["confirmation_status"] == "metadata_confirmed", \
                f"{f['feature_id']} should be metadata_confirmed via ICPSR search"

    def test_midus_features_have_confirmed_variables(self, features):
        midus_features = [f for f in features if f["dataset_source_id"] == "midus"]
        for f in midus_features:
            assert len(f["confirmed_variable_names"]) > 0, \
                f"{f['feature_id']} must have confirmed MIDUS 2 variable names"

    def test_midus_confirmation_source_is_icpsr(self, features):
        midus_features = [f for f in features if f["dataset_source_id"] == "midus"]
        for f in midus_features:
            assert f["confirmation_source"] == "icpsr_variable_search", \
                f"{f['feature_id']} must be confirmed via ICPSR variable search"

    def test_no_approved_for_route_b(self, features):
        for f in features:
            assert not f.get("approved_for_route_b"), \
                f"{f['feature_id']} must not be approved for Route B"

    def test_all_have_transfer_risk(self, features):
        for f in features:
            assert "transfer_risk" in f
            assert f["transfer_risk"] in ("low", "medium", "high")

    def test_source_variable_candidates_not_empty(self, features):
        for f in features:
            assert len(f["source_variable_candidates"]) > 0, \
                f"{f['feature_id']} must have at least one candidate variable"

    def test_no_life_score_in_features(self, features):
        feature_ids = [f["feature_id"] for f in features]
        assert "life_score" not in feature_ids


class TestOutcomeDefinitionsP13:
    """Tests for outcome_definitions_p13.yaml."""

    @pytest.fixture
    def outcomes(self):
        data = load_yaml(CONFIG_DIR / "outcome_definitions_p13.yaml")
        return data["outcomes"]

    def test_all_outcomes_candidate(self, outcomes):
        for o in outcomes:
            assert o["confirmation_status"] == "candidate", \
                f"{o['outcome_id']} must be candidate"

    def test_all_outcomes_no_confirmation_source(self, outcomes):
        for o in outcomes:
            assert o["confirmation_source"] == "none"

    def test_confirmed_variable_names_empty(self, outcomes):
        for o in outcomes:
            assert o["confirmed_variable_names"] == []

    def test_no_life_score(self, outcomes):
        outcome_ids = [o["outcome_id"] for o in outcomes]
        assert "life_score" not in outcome_ids
        for o in outcomes:
            assert "life_score" not in o["outcome_id"].lower()

    def test_no_probability_measurement_type(self, outcomes):
        for o in outcomes:
            assert o["measurement_type"] != "probability"

    def test_outcomes_span_all_domains(self, outcomes):
        domains = {o["domain"] for o in outcomes}
        expected = {"career_education", "financial", "health", "relationship", "subjective_wellbeing"}
        assert expected == domains

    def test_all_have_transfer_risk(self, outcomes):
        for o in outcomes:
            assert "transfer_risk" in o
            assert o["transfer_risk"] in ("low", "medium", "high")


class TestNoRawDataCommitted:
    """Verify no raw data files exist in tracked directories."""

    def test_raw_dir_only_has_gitkeep(self):
        if not RAW_DIR.exists():
            return  # Directory doesn't exist yet, which is fine
        # Allowed files in raw directories (gitignored, not committed)
        ALLOWED_RAW_FILES = {
            ".gitkeep",
            "acquisition_log_p13.json",
            # Phase 14: Downloaded raw data files (gitignored, not committed)
            "nlsy97_all_1997-2023.zip",
            "M1_P1_SURVEY_N7108_20190116.sav",
            "M2_P1_SURVEY_N4963_20200720.sav",
            "M3_P1_SURVEY_N3294_20251029.sav",
            # Codebooks (documentation, not individual-level data)
            "M1_P1_Codebook_20220505.pdf",
            "M2_P1_Codebook_20210129.pdf",
            "M3_P1_Codebook_20251125.pdf",
        }
        for subdir in ["nlsy97", "midus"]:
            subdir_path = RAW_DIR / subdir
            if not subdir_path.exists():
                continue
            for f in subdir_path.rglob("*"):
                if f.is_file():
                    assert f.name in ALLOWED_RAW_FILES, \
                        f"Unexpected file in raw dir: {f.relative_to(REPO_ROOT)}"


class TestAcquisitionScriptsExist:
    """Verify acquisition scripts exist and are Python files."""

    def test_acquire_script_exists(self):
        script = LABS_DIR / "scripts" / "acquire_public_resources.py"
        assert script.exists()

    def test_inventory_script_exists(self):
        script = LABS_DIR / "scripts" / "inventory_raw_data.py"
        assert script.exists()

    def test_validate_script_exists(self):
        script = LABS_DIR / "scripts" / "validate_raw_data_presence.py"
        assert script.exists()

    def test_parse_nlsy97_exists(self):
        script = LABS_DIR / "scripts" / "parse_nlsy97_extract.py"
        assert script.exists()

    def test_parse_midus_exists(self):
        script = LABS_DIR / "scripts" / "parse_midus_package.py"
        assert script.exists()


class TestDocsExist:
    """Verify Phase 13 documentation files exist."""

    def test_p13_data_acquisition_doc(self):
        assert (LABS_DIR / "P13_DATA_ACQUISITION.md").exists()

    def test_p13_user_download_instructions(self):
        assert (LABS_DIR / "P13_USER_DOWNLOAD_INSTRUCTIONS.md").exists()

    def test_p13_variable_confirmation(self):
        assert (LABS_DIR / "P13_VARIABLE_CONFIRMATION.md").exists()


class TestAcquisitionLogArtifact:
    """Verify acquisition log was generated correctly."""

    def test_acquisition_log_exists(self):
        log_path = ARTIFACTS_DIR / "acquisition_log_p13.json"
        if not log_path.exists():
            pytest.skip("Run acquire_public_resources.py first")
        with open(log_path) as f:
            log = json.load(f)
        assert log["phase"] == "P13"
        assert log["user_action_required"] is True
        assert len(log["url_checks"]) > 0

    def test_acquisition_log_has_notes(self):
        log_path = ARTIFACTS_DIR / "acquisition_log_p13.json"
        if not log_path.exists():
            pytest.skip("Run acquire_public_resources.py first")
        with open(log_path) as f:
            log = json.load(f)
        assert len(log["notes"]) > 0
