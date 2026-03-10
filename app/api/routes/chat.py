import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.api.schemas.chat import ChatRequest
from app.api.services.request_context import get_client_ip, get_request_source
from app.core import config
from app.services.hector_brain.orchestrator import HectorBrainOrchestrator

router = APIRouter()
brain = HectorBrainOrchestrator()


def is_rate_limited(client_ip: str) -> bool:
    now = time.time()
    window_start = now - 60

    if client_ip not in config.RATE_LIMIT_STORE:
        config.RATE_LIMIT_STORE[client_ip] = []

    config.RATE_LIMIT_STORE[client_ip] = [
        ts for ts in config.RATE_LIMIT_STORE[client_ip] if ts >= window_start
    ]

    if len(config.RATE_LIMIT_STORE[client_ip]) >= config.RATE_LIMIT_PER_MINUTE:
        return True

    config.RATE_LIMIT_STORE[client_ip].append(now)
    return False


def update_processing_metrics(processing_ms: int) -> None:
    config.TOTAL_PROCESSING_MS += processing_ms
    config.PROCESSING_TIMES.append(processing_ms)

    if processing_ms > config.MAX_PROCESSING_MS:
        config.MAX_PROCESSING_MS = processing_ms


@router.post("/chat")
def chat(req: ChatRequest, request: Request):
    config.CHAT_REQUEST_COUNT += 1
    config.REQUEST_TIMESTAMPS.append(time.time())

    request_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time())
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    start_processing = time.time()

    client_ip = get_client_ip(request)
    request_source = get_request_source(request)

    pergunta = req.pergunta or ""
    pergunta = pergunta.strip()

    if is_rate_limited(client_ip):
        config.CHAT_ERROR_COUNT += 1

        processing_ms = int((time.time() - start_processing) * 1000)
        update_processing_metrics(processing_ms)

        server_uptime = int(time.time() - config.START_TIME)

        return {
            "status": "error",
            "api_version": config.API_VERSION,
            "request_id": request_id,
            "timestamp": timestamp,
            "timestamp_iso": timestamp_iso,
            "processing_ms": processing_ms,
            "openai_latency_ms": 0,
            "server_uptime": server_uptime,
            "chat_requests_total": config.CHAT_REQUEST_COUNT,
            "engine": config.ENGINE_NAME,
            "engine_version": config.ENGINE_VERSION,
            "build_version": config.BUILD_VERSION,
            "model": config.OPENAI_MODEL,
            "request_source": request_source,
            "pergunta": req.pergunta,
            "question_length": len(pergunta),
            "tokens_input": 0,
            "tokens_output": 0,
            "tokens_total": 0,
            "erro": "rate_limit_exceeded",
        }

    if pergunta == "":
        config.CHAT_ERROR_COUNT += 1

        processing_ms = int((time.time() - start_processing) * 1000)
        update_processing_metrics(processing_ms)

        server_uptime = int(time.time() - config.START_TIME)

        return {
            "status": "error",
            "api_version": config.API_VERSION,
            "request_id": request_id,
            "timestamp": timestamp,
            "timestamp_iso": timestamp_iso,
            "processing_ms": processing_ms,
            "openai_latency_ms": 0,
            "server_uptime": server_uptime,
            "chat_requests_total": config.CHAT_REQUEST_COUNT,
            "engine": config.ENGINE_NAME,
            "engine_version": config.ENGINE_VERSION,
            "build_version": config.BUILD_VERSION,
            "model": config.OPENAI_MODEL,
            "request_source": request_source,
            "pergunta": req.pergunta,
            "question_length": 0,
            "tokens_input": 0,
            "tokens_output": 0,
            "tokens_total": 0,
            "erro": "pergunta_vazia",
        }

    try:
        brain_result = brain.process(pergunta)

        brain_classification = brain_result.classification.model_dump()
        brain_intent = brain_result.intent.model_dump()
        brain_routing = brain_result.routing.model_dump()
        brain_execution_plan = brain_result.execution_plan.model_dump()

        resposta = brain_result.final_answer

        processing_ms = int((time.time() - start_processing) * 1000)
        update_processing_metrics(processing_ms)

        config.CHAT_SUCCESS_COUNT += 1
        config.TOTAL_RESPONSE_CHARS += len(str(resposta))

        question_length = len(pergunta)
        response_length = len(str(resposta))
        server_uptime = int(time.time() - config.START_TIME)

        return {
            "status": "ok",
            "api_version": config.API_VERSION,
            "request_id": request_id,
            "timestamp": timestamp,
            "timestamp_iso": timestamp_iso,
            "processing_ms": processing_ms,
            "openai_latency_ms": 0,
            "server_uptime": server_uptime,
            "chat_requests_total": config.CHAT_REQUEST_COUNT,
            "engine": config.ENGINE_NAME,
            "engine_version": config.ENGINE_VERSION,
            "build_version": config.BUILD_VERSION,
            "model": config.OPENAI_MODEL,
            "request_source": request_source,
            "pergunta": pergunta,
            "question_length": question_length,
            "response_length": response_length,
            "tokens_input": 0,
            "tokens_output": 0,
            "tokens_total": 0,
            "brain": {
                "classification": brain_classification,
                "intent": brain_intent,
                "routing": brain_routing,
                "execution_plan": brain_execution_plan,
            },
            "resposta": resposta,
        }

    except Exception as e:
        config.CHAT_ERROR_COUNT += 1
        config.OPENAI_STATUS = "error"

        processing_ms = int((time.time() - start_processing) * 1000)
        update_processing_metrics(processing_ms)

        question_length = len(pergunta)
        server_uptime = int(time.time() - config.START_TIME)

        return {
            "status": "error",
            "api_version": config.API_VERSION,
            "request_id": request_id,
            "timestamp": timestamp,
            "timestamp_iso": timestamp_iso,
            "processing_ms": processing_ms,
            "openai_latency_ms": 0,
            "server_uptime": server_uptime,
            "chat_requests_total": config.CHAT_REQUEST_COUNT,
            "engine": config.ENGINE_NAME,
            "engine_version": config.ENGINE_VERSION,
            "build_version": config.BUILD_VERSION,
            "model": config.OPENAI_MODEL,
            "request_source": request_source,
            "pergunta": pergunta,
            "question_length": question_length,
            "tokens_input": 0,
            "tokens_output": 0,
            "tokens_total": 0,
            "erro": str(e),
        }
