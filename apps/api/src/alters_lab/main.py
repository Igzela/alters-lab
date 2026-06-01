import importlib
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from alters_lab.errors import AppError
from alters_lab.logging_config import setup_logging
from alters_lab.middleware import RateLimitMiddleware
from alters_lab.services.local_app import configure_frontend_static

# All API router modules. Each must export a `router` attribute.
_ROUTER_MODULES = [
    "alters",
    "archive_mechanism",
    "branches",
    "calibration_loop",
    "checkpoint_regeneration",
    "cycle_summary",
    "draft_review",
    "evidence_reports",
    "promotion_execution_gate",
    "promotion_live_execution",
    "promotion_orchestration",
    "phase3_closeout",
    "phase4_closeout",
    "phase5_closeout",
    "phase6_closeout",
    "generation_drafts",
    "rubric_delta",
    "snapshot_intake",
    "alter_dialogue",
    "product_surface",
    "provider_gateway",
    "provider_dialogue",
    "provider_dialogue_preview",
    "provider_adapter",
    "provider_connectivity",
    "provider_config",
    "p6_provider_policy",
    "storage_boundary",
    "user_workflow",
    "obsidian_weekly_note",
    "weekly_review_session",
    "weekly_review_assistant",
    "action_alignment",
    "self_deception_challenge",
    "alter_recommendation",
    "weekly_reminder",
    "pattern_review",
    "p6_data_retention",
    "behavior_validation",
    "runtime_layout",
    "local_app",
    "trend_analysis",
    "dynamic_weight",
    "pattern_adjustment",
    "behavior_metrics",
    "behavior_metric_trend",
]

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


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    request_id = request.headers.get("x-request-id", str(uuid.uuid4())[:8])
    logger.warning(
        "app_error status=%d code=%s path=%s request_id=%s msg=%s",
        exc.status_code,
        exc.error_code,
        request.url.path,
        request_id,
        exc.message,
    )
    body = exc.to_response()
    body["request_id"] = request_id
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = request.headers.get("x-request-id", str(uuid.uuid4())[:8])
    logger.exception(
        "unhandled_error path=%s request_id=%s",
        request.url.path,
        request_id,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred.",
            "request_id": request_id,
        },
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "alters-lab-api"}


for module_name in _ROUTER_MODULES:
    mod = importlib.import_module(f"alters_lab.api.{module_name}")
    app.include_router(mod.router)
configure_frontend_static(app)
