from fastapi import FastAPI

app = FastAPI(title="Alters Lab API")


@app.get("/health")
def health():
    return {"status": "ok", "service": "alters-lab-api"}
