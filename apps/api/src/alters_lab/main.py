from fastapi import FastAPI

from alters_lab.api.alters import router as alters_router
from alters_lab.api.branches import router as branches_router
from alters_lab.api.cycle_summary import router as cycle_summary_router
from alters_lab.api.draft_review import router as draft_review_router
from alters_lab.api.evidence_reports import router as evidence_reports_router
from alters_lab.api.promotion_execution_gate import router as promotion_execution_gate_router
from alters_lab.api.promotion_orchestration import router as promotion_orchestration_router
from alters_lab.api.generation_drafts import router as generation_drafts_router
from alters_lab.api.snapshot_intake import router as snapshot_intake_router

app = FastAPI(title="Alters Lab API")


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
