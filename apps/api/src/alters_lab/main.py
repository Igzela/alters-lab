import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from alters_lab.logging_config import setup_logging
from alters_lab.middleware import RateLimitMiddleware
from alters_lab.api.alters import router as alters_router
from alters_lab.api.archive_mechanism import router as archive_mechanism_router
from alters_lab.api.branches import router as branches_router
from alters_lab.api.calibration_loop import router as calibration_loop_router
from alters_lab.api.checkpoint_regeneration import router as checkpoint_regeneration_router
from alters_lab.api.cycle_summary import router as cycle_summary_router
from alters_lab.api.draft_review import router as draft_review_router
from alters_lab.api.evidence_reports import router as evidence_reports_router
from alters_lab.api.promotion_execution_gate import router as promotion_execution_gate_router
from alters_lab.api.promotion_live_execution import router as promotion_live_execution_router
from alters_lab.api.promotion_orchestration import router as promotion_orchestration_router
from alters_lab.api.phase4_closeout import router as phase4_closeout_router
from alters_lab.api.phase3_closeout import router as phase3_closeout_router
from alters_lab.api.generation_drafts import router as generation_drafts_router
from alters_lab.api.rubric_delta import router as rubric_delta_router
from alters_lab.api.snapshot_intake import router as snapshot_intake_router
from alters_lab.api.alter_dialogue import router as alter_dialogue_router
from alters_lab.api.product_surface import router as product_surface_router
from alters_lab.api.provider_gateway import router as provider_gateway_router
from alters_lab.api.provider_dialogue import router as provider_dialogue_router
from alters_lab.api.storage_boundary import router as storage_boundary_router
from alters_lab.api.user_workflow import router as user_workflow_router
from alters_lab.api.phase5_closeout import router as phase5_closeout_router
from alters_lab.api.obsidian_weekly_note import router as obsidian_weekly_note_router
from alters_lab.api.weekly_review_session import router as weekly_review_session_router
from alters_lab.api.action_alignment import router as action_alignment_router
from alters_lab.api.self_deception_challenge import router as self_deception_challenge_router
from alters_lab.api.alter_recommendation import router as alter_recommendation_router
from alters_lab.api.weekly_reminder import router as weekly_reminder_router
from alters_lab.api.pattern_review import router as pattern_review_router
from alters_lab.api.p6_data_retention import router as p6_data_retention_router
from alters_lab.api.p6_provider_policy import router as p6_provider_policy_router
from alters_lab.api.behavior_validation import router as behavior_validation_router
from alters_lab.api.phase6_closeout import router as phase6_closeout_router
from alters_lab.api.runtime_layout import router as runtime_layout_router
from alters_lab.api.local_app import router as local_app_router
from alters_lab.api.provider_adapter import router as provider_adapter_router
from alters_lab.api.provider_connectivity import router as provider_connectivity_router
from alters_lab.api.provider_config import router as provider_config_router
from alters_lab.api.provider_dialogue_preview import router as provider_dialogue_preview_router
from alters_lab.api.weekly_review_assistant import router as weekly_review_assistant_router
from alters_lab.api.trend_analysis import router as trend_analysis_router
from alters_lab.api.dynamic_weight import router as dynamic_weight_router
from alters_lab.api.pattern_adjustment import router as pattern_adjustment_router
from alters_lab.services.local_app import configure_frontend_static

logger = logging.getLogger("alters_lab")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Alters Lab API starting")
    yield
    logger.info("Alters Lab API shutting down")


app = FastAPI(
    title="Alters Lab API",
    description="Personal future-branch simulation and calibration system",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, max_requests=600, window_seconds=60)


@app.get("/health")
def health():
    return {"status": "ok", "service": "alters-lab-api"}


app.include_router(snapshot_intake_router)
app.include_router(cycle_summary_router)
app.include_router(evidence_reports_router)
app.include_router(branches_router)
app.include_router(alters_router)
app.include_router(generation_drafts_router)
app.include_router(draft_review_router)
app.include_router(promotion_orchestration_router)
app.include_router(promotion_execution_gate_router)
app.include_router(promotion_live_execution_router)
app.include_router(phase3_closeout_router)
app.include_router(alter_dialogue_router)
app.include_router(calibration_loop_router)
app.include_router(rubric_delta_router)
app.include_router(archive_mechanism_router)
app.include_router(checkpoint_regeneration_router)
app.include_router(phase4_closeout_router)
app.include_router(product_surface_router)
app.include_router(provider_gateway_router)
app.include_router(provider_dialogue_router)
app.include_router(storage_boundary_router)
app.include_router(user_workflow_router)
app.include_router(phase5_closeout_router)
app.include_router(obsidian_weekly_note_router)
app.include_router(weekly_review_session_router)
app.include_router(action_alignment_router)
app.include_router(self_deception_challenge_router)
app.include_router(alter_recommendation_router)
app.include_router(weekly_reminder_router)
app.include_router(pattern_review_router)
app.include_router(p6_data_retention_router)
app.include_router(p6_provider_policy_router)
app.include_router(behavior_validation_router)
app.include_router(phase6_closeout_router)
app.include_router(runtime_layout_router)
app.include_router(local_app_router)
app.include_router(provider_adapter_router)
app.include_router(provider_connectivity_router)
app.include_router(provider_config_router)
app.include_router(provider_dialogue_preview_router)
app.include_router(weekly_review_assistant_router)
app.include_router(trend_analysis_router)
app.include_router(dynamic_weight_router)
app.include_router(pattern_adjustment_router)
configure_frontend_static(app)
