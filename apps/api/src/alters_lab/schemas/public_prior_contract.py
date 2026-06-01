"""Public-prior integration contract — defines how population baselines may enter forecasts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# --- Module-level constants for import by services ---

ALLOWED_OUTPUT_FIELDS: tuple[str, ...] = (
    "prior_direction",
    "probability_band",
    "population_percentile",
    "deviation_from_baseline",
    "confidence",
    "transfer_risk",
    "explanation",
    "limitations",
)

REQUIRED_GUARDS: tuple[str, ...] = (
    "model_card_required",
    "approved_for_route_b_required",
    "transfer_risk_required",
    "no_exact_probability_without_calibration",
    "no_override_of_personal_evidence",
    "calibration_layer_required",
)

DISALLOWED_BEHAVIORS: tuple[str, ...] = (
    "direct_individual_destiny_prediction",
    "hidden_model_output",
    "exact_probability_without_model_card",
    "bypass_forecast_snapshot",
    "bypass_external_evidence",
    "bypass_forecast_evaluation",
    "overwrite_action_alignment",
)


class PublicPriorIntegrationContract(BaseModel):
    """Contract defining how population baseline outputs enter the main forecast system."""

    model_config = ConfigDict(extra="forbid")

    contract_id: str
    version: str
    allowed_input_artifacts: list[str] = Field(default_factory=list)
    allowed_output_fields: list[str] = Field(
        default_factory=lambda: list(ALLOWED_OUTPUT_FIELDS)
    )
    required_guards: list[str] = Field(
        default_factory=lambda: list(REQUIRED_GUARDS)
    )
    disallowed_behaviors: list[str] = Field(
        default_factory=lambda: list(DISALLOWED_BEHAVIORS)
    )
