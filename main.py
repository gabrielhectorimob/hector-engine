from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
import httpx
import time
import uuid
import psutil
import threading
from datetime import datetime, timezone

app = FastAPI()

API_VERSION = "1.0"
ENGINE_NAME = "hector-engine"
ENGINE_VERSION = "1.0"
OPENAI_MODEL = "gpt-4.1-mini"
BUILD_VERSION = os.getenv("BUILD_VERSION", "dev")

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

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))

CHAT_REQUEST_COUNT = 0
CHAT_SUCCESS_COUNT = 0
CHAT_ERROR_COUNT = 0

TOTAL_PROCESSING_MS = 0
TOTAL_RESPONSE_CHARS = 0
MAX_PROCESSING_MS = 0

PROCESSING_TIMES = []
OPENAI_LATENCIES = []
REQUEST_TIMESTAMPS = []
RATE_LIMIT_STORE = {}

OPENAI_STATUS = "unknown"


class ChatRequest(BaseModel):
    pergunta: str


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        parts = [p.strip() for p in forwarded_for.split(",") if p.strip()]
        if parts:
            return parts[0]

    real_ip = request.headers.get("x-real-ip")

    if real_ip:
        return real_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def get_request_source(request: Request) -> str:
    source = request.headers.get("x-request-source", "").strip()

    if source:
        return source

    return "unknown"


def is_rate_limited(client_ip: str) -> bool:

    now = time.time()
    window_start = now - 60

    if client_ip not in RATE_LIMIT_STORE:
        RATE_LIMIT_STORE[client_ip] = []

    RATE_LIMIT_STORE[client_ip] = [
        ts for ts in RATE_LIMIT_STORE[client_ip] if ts >= window_start
    ]

    if len(RATE_LIMIT_STORE[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        return True

    RATE_LIMIT_STORE[client_ip].append(now)

    return False


def update_processing_metrics(processing_ms: int):

    global TOTAL_PROCESSING_MS
    global MAX_PROCESSING_MS

    TOTAL_PROCESSING_MS += processing_ms
    PROCESSING_TIMES.append(processing_ms)

    if processing_ms > MAX_PROCESSING_MS:
        MAX_PROCESSING_MS = processing_ms


def compute_p95(values):

    if not values:
        return 0

    sorted_values = sorted(values)
    index = int(len(sorted_values) * 0.95) - 1
    index = max(index, 0)

    return sorted_values[index]


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/health")
def health():

    return {
        "server": "ok",
        "openai_key_loaded": bool(OPENAI_API_KEY),
        "openai_status": OPENAI_STATUS
    }


@app.get("/engine")
def engine():

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "build_version": BUILD_VERSION,
        "model": OPENAI_MODEL
    }


@app.get("/metrics")
def metrics():

    uptime = int(time.time() - START_TIME)

    avg_processing_ms = 0

    if CHAT_REQUEST_COUNT > 0:
        avg_processing_ms = int(TOTAL_PROCESSING_MS / CHAT_REQUEST_COUNT)

    requests_per_minute = 0

    if uptime > 0:
        requests_per_minute = round((CHAT_REQUEST_COUNT / uptime) * 60, 2)

    success_rate = 0

    if CHAT_REQUEST_COUNT > 0:
        success_rate = round(CHAT_SUCCESS_COUNT / CHAT_REQUEST_COUNT, 4)

    error_rate = 0

    if CHAT_REQUEST_COUNT > 0:
        error_rate = round(CHAT_ERROR_COUNT / CHAT_REQUEST_COUNT, 4)

    avg_response_length = 0

    if CHAT_SUCCESS_COUNT > 0:
        avg_response_length = int(TOTAL_RESPONSE_CHARS / CHAT_SUCCESS_COUNT)

    p95_processing_ms = compute_p95(PROCESSING_TIMES)
    openai_latency_p95 = compute_p95(OPENAI_LATENCIES)

    now = time.time()
    window_start = now - 60

    requests_last_60s = len(
        [ts for ts in REQUEST_TIMESTAMPS if ts >= window_start]
    )

    process = psutil.Process(os.getpid())

    engine_memory_mb = round(
        process.memory_info().rss / 1024 / 1024,
        2
    )

    engine_cpu_percent = round(
        process.cpu_percent(interval=None),
        2
    )

    engine_threads = threading.active_count()

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "build_version": BUILD_VERSION,
        "model": OPENAI_MODEL,
        "engine_instance_id": ENGINE_INSTANCE_ID,
        "engine_started_at": ENGINE_STARTED_AT,
        "uptime_seconds": uptime,
        "chat_requests_total": CHAT_REQUEST_COUNT,
        "chat_success_total": CHAT_SUCCESS_COUNT,
        "chat_errors_total": CHAT_ERROR_COUNT,
        "avg_processing_ms": avg_processing_ms,
        "max_processing_ms": MAX_PROCESSING_MS,
        "p95_processing_ms": p95_processing_ms,
        "openai_latency_p95": openai_latency_p95,
        "requests_last_60s": requests_last_60s,
        "requests_per_minute": requests_per_minute,
        "success_rate": success_rate,
        "error_rate": error_rate,
        "avg_response_length": avg_response_length,
        "engine_memory_mb": engine_memory_mb,
        "engine_cpu_percent": engine_cpu_percent,
        "engine_threads": engine_threads,
        "rate_limit_per_minute": RATE_LIMIT_PER_MINUTE,
        "openai_status": OPENAI_STATUS
    }


@app.post("/chat")
def chat(req: ChatRequest, request: Request):

    global CHAT_REQUEST_COUNT
    global CHAT_SUCCESS_COUNT
    global CHAT_ERROR_COUNT
    global TOTAL_RESPONSE_CHARS
    global OPENAI_STATUS

    CHAT_REQUEST_COUNT += 1
    REQUEST_TIMESTAMPS.append(time.time())

    request_id = str(uuid.uuid4())[:8]

    timestamp = int(time.time())
    timestamp_iso = datetime.now(timezone.utc).isoformat()

    start_processing = time.time()

    client_ip = get_client_ip(request)
    request_source = get_request_source(request)

    pergunta = req.pergunta or ""
    pergunta = pergunta.strip()

    if is_rate_limited(client_ip):

        CHAT_ERROR_COUNT += 1

        processing_ms = int((time.time() - start_processing) * 1000)

        update_processing_metrics(processing_ms)

        server_uptime = int(time.time() - START_TIME)

        return {
            "status": "error",
            "api_version": API_VERSION,
            "request_id": request_id,
            "timestamp": timestamp,
            "timestamp_iso": timestamp_iso,
            "processing_ms": processing_ms,
            "openai_latency_ms": 0,
            "server_uptime": server_uptime,
            "chat_requests_total": CHAT_REQUEST_COUNT,
            "engine": ENGINE_NAME,
            "engine_version": ENGINE_VERSION,
            "build_version": BUILD_VERSION,
            "model": OPENAI_MODEL,
            "request_source": request_source,
            "pergunta": req.pergunta,
            "question_length": len(pergunta),
            "tokens_input": 0,
            "tokens_output": 0,
            "tokens_total": 0,
            "erro": "rate_limit_exceeded"
        }

    if pergunta == "":

        CHAT_ERROR_COUNT += 1

        processing_ms = int((time.time() - start_processing) * 1000)

        update_processing_metrics(processing_ms)

        server_uptime = int(time.time() - START_TIME)

        return {
            "status": "error",
            "api_version": API_VERSION,
            "request_id": request_id,
            "timestamp": timestamp,
            "timestamp_iso": timestamp_iso,
            "processing_ms": processing_ms,
            "openai_latency_ms": 0,
            "server_uptime": server_uptime,
            "chat_requests_total": CHAT_REQUEST_COUNT,
            "engine": ENGINE_NAME,
            "engine_version": ENGINE_VERSION,
            "build_version": BUILD_VERSION,
            "model": OPENAI_MODEL,
            "request_source": request_source,
            "pergunta": req.pergunta,
            "question_length": 0,
            "tokens_input": 0,
            "tokens_output": 0,
            "tokens_total": 0,
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

        openai_start = time.time()

        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                OPENAI_URL,
                headers=headers,
                json=payload
            )

        openai_latency_ms = int(
            (time.time() - openai_start) * 1000
        )

        OPENAI_LATENCIES.append(openai_latency_ms)
        OPENAI_STATUS = "ok"

        data = r.json()

        resposta = ""

        if "output" in data:
            try:
                resposta = data["output"][0]["content"][0]["text"]
            except Exception:
                resposta = str(data)
        else:
            resposta = str(data)

        usage = data.get("usage", {})

        tokens_input = usage.get("input_tokens", 0)
        tokens_output = usage.get("output_tokens", 0)
        tokens_total = usage.get("total_tokens", 0)

        processing_ms = int(
            (time.time() - start_processing) * 1000
        )

        update_processing_metrics(processing_ms)

        CHAT_SUCCESS_COUNT += 1

        TOTAL_RESPONSE_CHARS += len(resposta)

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
            "openai_latency_ms": openai_latency_ms,
            "server_uptime": server_uptime,
            "chat_requests_total": CHAT_REQUEST_COUNT,
            "engine": ENGINE_NAME,
            "engine_version": ENGINE_VERSION,
            "build_version": BUILD_VERSION,
            "model": OPENAI_MODEL,
            "request_source": request_source,
            "pergunta": pergunta,
            "question_length": question_length,
            "response_length": response_length,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "tokens_total": tokens_total,
            "resposta": resposta
        }

    except Exception as e:

        CHAT_ERROR_COUNT += 1

        OPENAI_STATUS = "error"

        processing_ms = int(
            (time.time() - start_processing) * 1000
        )

        update_processing_metrics(processing_ms)

        question_length = len(pergunta)

        server_uptime = int(time.time() - START_TIME)

        return {
            "status": "error",
            "api_version": API_VERSION,
            "request_id": request_id,
            "timestamp": timestamp,
            "timestamp_iso": timestamp_iso,
            "processing_ms": processing_ms,
            "openai_latency_ms": 0,
            "server_uptime": server_uptime,
            "chat_requests_total": CHAT_REQUEST_COUNT,
            "engine": ENGINE_NAME,
            "engine_version": ENGINE_VERSION,
            "build_version": BUILD_VERSION,
            "model": OPENAI_MODEL,
            "request_source": request_source,
            "pergunta": pergunta,
            "question_length": question_length,
            "tokens_input": 0,
            "tokens_output": 0,
            "tokens_total": 0,
            "erro": str(e)
        }
