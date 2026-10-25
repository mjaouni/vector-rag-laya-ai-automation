"""FastAPI entry point. Local-development example, not internet-facing."""
from __future__ import annotations
import hmac
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from service.config import ROOT, settings
from service.pipeline import process_question
from service.decisions import classify
from service.retrieval import retrieve, qdrant, close_qdrant
from service.notify import send_notification

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        close_qdrant()


app = FastAPI(title="Vector RAG + Laya + Ollama + n8n", version="1.0.1", lifespan=lifespan)

class Query(BaseModel):
    message: str = Field(min_length=3, max_length=4000)
    request_id: str | None = Field(default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")

class Notification(BaseModel):
    request_id: str
    status: str
    answer: str
    sources: list[str] = Field(default_factory=list)
    reason: str = ""


def auth(x_demo_token: str | None = Header(default=None)):
    if not x_demo_token or not hmac.compare_digest(x_demo_token, settings.workflow_token):
        raise HTTPException(401, detail="X-Demo-Token missing or invalid. See .env and n8n README.")

@app.get("/")
def home():
    return FileResponse(ROOT / "web.html")

@app.get("/healthz")
def healthz():
    return {"ok": True, "service": "vector-rag-laya", "decision_provider":settings.decision_provider,
            "ollama_model":settings.ollama_model}

@app.get("/api/status")
def status():
    try:
        ready = qdrant().collection_exists(settings.collection)
    except Exception:
        ready = False
    return {"indexed": ready, "collection":settings.collection, "decision_provider": settings.decision_provider,
            "ollama_model":settings.ollama_model, "note":"status does not load Laya or test Ollama connectivity"}

@app.post("/api/process", dependencies=[Depends(auth)])
def process(data: Query):
    return process_question(data.message, request_id=data.request_id)

@app.post("/api/classify", dependencies=[Depends(auth)])
def classification(data: Query):
    try:
        return classify(data.message)
    except Exception as exc:
        raise HTTPException(503, detail=f"Laya unavailable: {type(exc).__name__}. Check server logs or use DECISION_PROVIDER=rules to diagnose.") from exc

@app.post("/api/retrieve", dependencies=[Depends(auth)])
def search(data: Query):
    try:
        return {"hits":retrieve(data.message)}
    except Exception as exc:
        raise HTTPException(503, detail=f"Retrieval unavailable: {type(exc).__name__}. Seed the knowledge base before starting API.") from exc

@app.post("/api/notify", dependencies=[Depends(auth)])
def notify(data: Notification):
    try:
        return send_notification(data.model_dump())
    except (OSError, ValueError) as exc:
        raise HTTPException(503, detail=f"Notification unavailable: {type(exc).__name__}. Check SMTP configuration.") from exc

@app.post("/api/via-n8n", dependencies=[Depends(auth)])
def via_n8n(data: Query):
    # Fixed configured destination; user cannot supply an arbitrary URL.
    try:
        with httpx.Client(timeout=180.0) as client:
            response = client.post(settings.n8n_webhook_url, json=data.model_dump(exclude_none=True))
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(502, detail=f"n8n webhook unavailable or not active: {type(exc).__name__}") from exc
