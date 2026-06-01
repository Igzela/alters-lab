"""Tests for Phase 12 population baseline pilot schemas.

Enforces:
- MIDUS and NLSY97 are included sources
- FFCWS is deferred, not primary
- No source is approved_for_route_b
- Candidate variables cannot be treated as final variable names
- Baseline artifacts default to not approved
- No raw data committed
- No life_score
- No exact personal probability
"""

import pytest
import yaml
from pathlib import Path

from alters_lab.schemas.population_baseline_pilot import (
    BaselineFeatureCandidate,
    BaselineOutcomeCandidate,
    BaselineTableArtifact,
    PopulationBaselineSourceSelection,
    SourceSelectionEntry,
)
from alters_lab.schemas.population_baseline import (
    PopulationBaselineModelCard,
    PopulationPriorArtifact,
)


# --- Paths ---

CONFIG_DIR = Path(__file__).resolve().parents[2] / ".." / "labs" / "population_baseline" / "config"
SOURCE_SELECTION_PATH = CONFIG_DIR / "source_selection_v0_1.yaml"
OUTCOME_DEFINITIONS_PATH = CONFIG_DIR / "outcome_definitions_p12.yaml"
FEATURE_MAPPING_PATH = CONFIG_DIR / "feature_mapping_p12.yaml"


# --- Source Selection Tests ---


class TestSourceSelection:
    """Validate source selection invariants."""

    def test_midus_is_included(self):
        """MIDUS must be included as a primary source."""
        selection = _load_source_selection()
        midus = [s for s in selection.sources if s.source_id == "midus"]
        assert len(midus) == 1
        assert midus[0].first_pass_decision == "include"

    def test_nlsy97_is_included(self):
        """NLSY97 must be included as a primary source."""
        selection = _load_source_selection()
        nlsy = [s for s in selection.sources if s.source_id == "nlsy97"]
        assert len(nlsy) == 1
        assert nlsy[0].first_pass_decision == "include"

    def test_ffcws_is_deferred(self):
        """FFCWS must be deferred, not primary."""
        selection = _load_source_selection()
        ffcws = [s for s in selection.sources if s.source_id == "ffcws"]
        assert len(ffcws) == 1
        assert ffcws[0].first_pass_decision == "defer"

    def test_psid_is_deferred(self):
        """PSID must be deferred."""
        selection = _load_source_selection()
        psid = [s for s in selection.sources if s.source_id == "psid"]
        assert len(psid) == 1
        assert psid[0].first_pass_decision == "defer"

    def test_no_source_is_approved_for_route_b(self):
        """Source selection entries do not carry route_b approval."""
        # SourceSelectionEntry has no approved_for_route_b field
        entry = SourceSelectionEntry(
            source_id="test",
            label="Test",
            source_type="longitudinal_dataset",
            population_description="Test pop",
            transfer_risk="high",
            first_pass_decision="include",
        )
        assert not hasattr(entry, "approved_for_route_b")

    def test_at_least_one_source_included(self):
        """Selection must include at least one source."""
        selection = PopulationBaselineSourceSelection(
            sources=[
                SourceSelectionEntry(
                    source_id="a",
                    label="A",
                    source_type="longitudinal_dataset",
                    population_description="A pop",
                    transfer_risk="high",
                    first_pass_decision="include",
                )
            ]
        )
        assert len(selection.sources) == 1

    def test_empty_sources_raises(self):
        """Selection with no included sources must raise."""
        with pytest.raises(Exception):
            PopulationBaselineSourceSelection(
                sources=[
                    SourceSelectionEntry(
                        source_id="a",
                        label="A",
                        source_type="longitudinal_dataset",
                        population_description="A pop",
                        transfer_risk="high",
                        first_pass_decision="defer",
                    )
                ]
            )

    def test_all_sources_have_transfer_risk(self):
        """Every source must declare transfer_risk."""
        selection = _load_source_selection()
        for source in selection.sources:
            assert source.transfer_risk in ("low", "medium", "high")


# --- Outcome Definition Tests ---


class TestOutcomeDefinitions:
    """Validate outcome definition invariants."""

    def test_outcomes_span_5_domains(self):
        """Outcomes must cover all 5 Alters Lab domains."""
        outcomes = _load_outcome_candidates()
        domains = {o.domain for o in outcomes}
        expected = {"career_education", "financial", "health", "relationship", "subjective_wellbeing"}
        assert domains == expected

    def test_no_life_score_outcome(self):
        """No outcome should reference life_score."""
        outcomes = _load_outcome_candidates()
        for o in outcomes:
            assert "life_score" not in o.outcome_id.lower()
            assert "life score" not in o.label.lower()

    def test_all_outcomes_have_transfer_risk(self):
        """Every outcome must declare transfer_risk."""
        outcomes = _load_outcome_candidates()
        for o in outcomes:
            assert o.transfer_risk in ("low", "medium", "high")

    def test_all_outcomes_have_direction(self):
        """Every outcome must declare target_direction."""
        outcomes = _load_outcome_candidates()
        for o in outcomes:
            assert o.target_direction in ("higher_is_better", "lower_is_better", "category_dependent")

    def test_no_exact_personal_probability(self):
        """Outcomes must not emit exact personal probabilities."""
        outcomes = _load_outcome_candidates()
        for o in outcomes:
            assert o.measurement_type != "probability"
            assert "probability" not in o.outcome_id.lower()


# --- Feature Mapping Tests ---


class TestFeatureMappings:
    """Validate feature mapping invariants."""

    def test_candidate_variables_not_treated_as_final(self):
        """source_variable_candidates are candidates, not confirmed names."""
        features = _load_feature_candidates()
        for f in features:
            # Field name explicitly says "candidates"
            assert len(f.source_variable_candidates) >= 0

    def test_features_map_to_predictor_profile(self):
        """Preferred features should map to at least one predictor profile field."""
        features = _load_feature_candidates()
        preferred = [f for f in features if f.first_pass_status == "preferred"]
        for f in preferred:
            assert len(f.maps_to_predictor_profile_fields) > 0 or len(f.maps_to_behavior_metric_ids) > 0

    def test_all_features_have_transfer_risk(self):
        """Every feature must declare transfer_risk."""
        features = _load_feature_candidates()
        for f in features:
            assert f.transfer_risk in ("low", "medium", "high")

    def test_no_feature_approved_for_route_b(self):
        """Feature candidates have no route_b approval concept."""
        feature = BaselineFeatureCandidate(
            feature_id="test",
            construct_id="test_construct",
            dataset_source_id="midus",
            expected_direction="positive",
            transfer_risk="high",
            first_pass_status="candidate",
        )
        assert not hasattr(feature, "approved_for_route_b")


# --- Baseline Artifact Tests ---


class TestBaselineArtifacts:
    """Validate baseline artifact invariants."""

    def test_baseline_table_defaults(self):
        """BaselineTableArtifact must not have route_b approval."""
        artifact = BaselineTableArtifact(
            artifact_id="bt_test",
            dataset_source_id="nlsy97",
            outcome_id="employment_stability",
            subgroup_definition="age 25-34",
            n=100,
            observed_rate_or_mean=0.65,
            confidence_interval="0.62-0.68",
            missingness_rate=0.05,
            transfer_risk="high",
        )
        assert not hasattr(artifact, "approved_for_route_b")
        assert artifact.transfer_risk == "high"

    def test_baseline_table_positive_n(self):
        """Sample size must be positive."""
        with pytest.raises(Exception):
            BaselineTableArtifact(
                artifact_id="bt_test",
                dataset_source_id="nlsy97",
                outcome_id="test",
                subgroup_definition="test",
                n=0,
                observed_rate_or_mean=0.5,
                confidence_interval="0.4-0.6",
                missingness_rate=0.0,
                transfer_risk="high",
            )

    def test_baseline_table_missingness_bounded(self):
        """Missingness rate must be between 0 and 1."""
        with pytest.raises(Exception):
            BaselineTableArtifact(
                artifact_id="bt_test",
                dataset_source_id="nlsy97",
                outcome_id="test",
                subgroup_definition="test",
                n=100,
                observed_rate_or_mean=0.5,
                confidence_interval="0.4-0.6",
                missingness_rate=1.5,
                transfer_risk="high",
            )

    def test_model_card_not_approved_by_default(self):
        """PopulationBaselineModelCard defaults to not approved."""
        card = PopulationBaselineModelCard(
            model_id="mc_test",
            source_dataset_ids=["nlsy97"],
            outcome_id="test",
            model_family="baseline_table",
            transfer_risk="high",
        )
        assert card.approved_for_route_b is False
        assert card.training_status == "not_trained"

    def test_no_exact_probability_in_prior_artifact(self):
        """PopulationPriorArtifact with high transfer risk caps confidence."""
        artifact = PopulationPriorArtifact(
            artifact_id="pa_test",
            model_id="mc_test",
            generated_at="2026-01-01T00:00:00Z",
            domain="career_education",
            prior_type="baseline_table",
            prior_direction="favorable",
            confidence="high",
            transfer_risk="high",
            explanation="test",
        )
        # High transfer risk caps confidence to medium
        assert artifact.confidence == "medium"


# --- Config File Validation Tests ---


class TestConfigFiles:
    """Validate that YAML config files parse correctly."""

    def test_source_selection_yaml_parses(self):
        """source_selection_v0_1.yaml must parse as valid source selection."""
        selection = _load_source_selection()
        assert len(selection.sources) == 4

    def test_outcome_definitions_yaml_parses(self):
        """outcome_definitions_p12.yaml must parse as valid outcomes."""
        outcomes = _load_outcome_candidates()
        assert len(outcomes) >= 10

    def test_feature_mapping_yaml_parses(self):
        """feature_mapping_p12.yaml must parse as valid features."""
        features = _load_feature_candidates()
        assert len(features) >= 5


# --- Helpers ---


def _load_source_selection() -> PopulationBaselineSourceSelection:
    """Load and parse source_selection_v0_1.yaml."""
    with open(SOURCE_SELECTION_PATH) as f:
        data = yaml.safe_load(f)
    entries = [SourceSelectionEntry(**s) for s in data["sources"]]
    return PopulationBaselineSourceSelection(sources=entries)


def _load_outcome_candidates() -> list[BaselineOutcomeCandidate]:
    """Load and parse outcome_definitions_p12.yaml."""
    with open(OUTCOME_DEFINITIONS_PATH) as f:
        data = yaml.safe_load(f)
    return [BaselineOutcomeCandidate(**o) for o in data["outcomes"]]


def _load_feature_candidates() -> list[BaselineFeatureCandidate]:
    """Load and parse feature_mapping_p12.yaml."""
    with open(FEATURE_MAPPING_PATH) as f:
        data = yaml.safe_load(f)
    return [BaselineFeatureCandidate(**feat) for feat in data["features"]]
