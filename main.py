from fastapi import FastAPI
from pydantic import BaseModel
import os
import httpx
import time
import uuid
from datetime import datetime, timezone

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
ENGINE_STARTED_AT = datetime.now(timezone.utc).isoformat()
ENGINE_INSTANCE_ID = str(uuid.uuid4())[:8]

CHAT_REQUEST_COUNT = 0
CHAT_ERROR_COUNT = 0
TOTAL_PROCESSING_MS = 0


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

    avg_processing_ms = 0
    if CHAT_REQUEST_COUNT > 0:
        avg_processing_ms = int(TOTAL_PROCESSING_MS / CHAT_REQUEST_COUNT)

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "model": OPENAI_MODEL,
        "engine_instance_id": ENGINE_INSTANCE_ID,
        "engine_started_at": ENGINE_STARTED_AT,
        "uptime_seconds": uptime,
        "chat_requests_total": CHAT_REQUEST_COUNT,
        "chat_errors_total": CHAT_ERROR_COUNT,
        "avg_processing_ms": avg_processing_ms
    }


@app.post("/chat")
def chat(req: ChatRequest):

    global CHAT_REQUEST_COUNT
    global CHAT_ERROR_COUNT
    global TOTAL_PROCESSING_MS

    CHAT_REQUEST_COUNT += 1

    request_id = str(uuid.uuid4())[:8]

    timestamp = int(time.time())
    timestamp_iso = datetime.now(timezone.utc).isoformat()

    start_processing = time.time()

    pergunta = req.pergunta or ""
    pergunta = pergunta.strip()

    if pergunta == "":
        CHAT_ERROR_COUNT += 1

        processing_ms = int((time.time() - start_processing) * 1000)
        TOTAL_PROCESSING_MS += processing_ms

        server_uptime = int(time.time() - START_TIME)

        return {
            "status": "error",
            "api_version": API_VERSION,
            "request_id": request_id,
            "timestamp": timestamp,
            "timestamp_iso": timestamp_iso,
            "processing_ms": processing_ms,
            "server_uptime": server_uptime,
            "chat_requests_total": CHAT_REQUEST_COUNT,
            "engine": ENGINE_NAME,
            "engine_version": ENGINE_VERSION,
            "model": OPENAI_MODEL,
            "pergunta": req.pergunta,
            "question_length": 0,
            "erro": "pergunta_vazia"
        }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENAI_MODEL,
        "input": pergunta
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(OPENAI_URL, headers=headers, json=payload)

        data = r.json()

        resposta = ""

        if "output" in data:
            try:
                resposta = data["output"][0]["content"][0]["text"]
            except Exception:
                resposta = str(data)
        else:
            resposta = str(data)

        processing_ms = int((time.time() - start_processing) * 1000)
        TOTAL_PROCESSING_MS += processing_ms

        question_length = len(pergunta)
        response_length = len(resposta)
        server_uptime = int(time.time() - START_TIME)

        return {
            "status": "ok",
            "api_version": API_VERSION,
            "request_id": request_id,
            "timestamp": timestamp,
            "timestamp_iso": timestamp_iso,
            "processing_ms": processing_ms,
            "server_uptime": server_uptime,
            "chat_requests_total": CHAT_REQUEST_COUNT,
            "engine": ENGINE_NAME,
            "engine_version": ENGINE_VERSION,
            "model": OPENAI_MODEL,
            "pergunta": pergunta,
            "question_length": question_length,
            "response_length": response_length,
            "resposta": resposta
        }

    except Exception as e:

        CHAT_ERROR_COUNT += 1

        processing_ms = int((time.time() - start_processing) * 1000)
        TOTAL_PROCESSING_MS += processing_ms

        question_length = len(pergunta)
        server_uptime = int(time.time() - START_TIME)

        return {
            "status": "error",
            "api_version": API_VERSION,
            "request_id": request_id,
            "timestamp": timestamp,
            "timestamp_iso": timestamp_iso,
            "processing_ms": processing_ms,
            "server_uptime": server_uptime,
            "chat_requests_total": CHAT_REQUEST_COUNT,
            "engine": ENGINE_NAME,
            "engine_version": ENGINE_VERSION,
            "model": OPENAI_MODEL,
            "pergunta": pergunta,
            "question_length": question_length,
            "erro": str(e)
        }
