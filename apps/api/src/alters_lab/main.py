from fastapi import FastAPI

from alters_lab.api.snapshot_intake import router as snapshot_intake_router

app = FastAPI(title="Alters Lab API")


@app.get("/health")
def health():
    return {"status": "ok", "service": "alters-lab-api"}


app.include_router(snapshot_intake_router)
