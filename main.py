from fastapi import FastAPI
from pydantic import BaseModel
import os
import httpx
import time
import uuid

app = FastAPI()

API_VERSION = "1.0"
ENGINE_NAME = "hector-engine"
ENGINE_VERSION = "1.0"
OPENAI_MODEL = "gpt-4.1-mini"

RAW_KEY = os.getenv("OPENAI_API_KEY", "")

OPENAI_API_KEY = (
    RAW_KEY
    .replace("\n", "")
    .replace("\r", "")
    .strip()
)

OPENAI_URL = "https://api.openai.com/v1/responses"

START_TIME = time.time()
CHAT_REQUEST_COUNT = 0


class ChatRequest(BaseModel):
    pergunta: str


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/health")
def health():
    return {
        "server": "ok",
        "openai_key_loaded": bool(OPENAI_API_KEY)
    }


@app.get("/engine")
def engine():
    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "model": OPENAI_MODEL
    }


@app.get("/metrics")
def metrics():
    uptime = int(time.time() - START_TIME)

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "model": OPENAI_MODEL,
        "uptime_seconds": uptime,
        "chat_requests_total": CHAT_REQUEST_COUNT
    }


@app.post("/chat")
def chat(req: ChatRequest):

    global CHAT_REQUEST_COUNT
    CHAT_REQUEST_COUNT += 1

    request_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time())

    start_processing = time.time()

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENAI_MODEL,
        "input": req.pergunta
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(OPENAI_URL, headers=headers, json=payload)

        data = r.json()

        resposta = ""

        if "output" in data:
            try:
                resposta = data["output"][0]["content"][0]["text"]
            except:
                resposta = str(data)
        else:
            resposta = str(data)

        processing_ms = int((time.time() - start_processing) * 1000)

        return {
            "status": "ok",
            "api_version": API_VERSION,
            "request_id": request_id,
            "timestamp": timestamp,
            "processing_ms": processing_ms,
            "engine": ENGINE_NAME,
            "engine_version": ENGINE_VERSION,
            "model": OPENAI_MODEL,
            "resposta": resposta
        }

    except Exception as e:

        processing_ms = int((time.time() - start_processing) * 1000)

        return {
            "status": "error",
            "api_version": API_VERSION,
            "request_id": request_id,
            "timestamp": timestamp,
            "processing_ms": processing_ms,
            "engine": ENGINE_NAME,
            "engine_version": ENGINE_VERSION,
            "model": OPENAI_MODEL,
            "erro": str(e)
        }
