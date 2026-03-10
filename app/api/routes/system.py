import os
import time
import threading
import psutil
from fastapi import APIRouter

from app.core import config

router = APIRouter()


def compute_p95(values):
    if not values:
        return 0

    sorted_values = sorted(values)
    index = int(len(sorted_values) * 0.95) - 1
    index = max(index, 0)

    return sorted_values[index]


@router.get("/")
def root():
    return {"status": "running"}


@router.get("/health")
def health():
    return {
        "server": "ok",
        "openai_key_loaded": bool(config.OPENAI_API_KEY),
        "openai_status": config.OPENAI_STATUS,
    }


@router.get("/engine")
def engine():
    return {
        "engine": config.ENGINE_NAME,
        "version": config.ENGINE_VERSION,
        "build_version": config.BUILD_VERSION,
        "model": config.OPENAI_MODEL,
    }


@router.get("/metrics")
def metrics():
    uptime = int(time.time() - config.START_TIME)

    avg_processing_ms = 0
    if config.CHAT_REQUEST_COUNT > 0:
        avg_processing_ms = int(
            config.TOTAL_PROCESSING_MS / config.CHAT_REQUEST_COUNT
        )

    requests_per_minute = 0
    if uptime > 0:
        requests_per_minute = round(
            (config.CHAT_REQUEST_COUNT / uptime) * 60,
            2,
        )

    success_rate = 0
    if config.CHAT_REQUEST_COUNT > 0:
        success_rate = round(
            config.CHAT_SUCCESS_COUNT / config.CHAT_REQUEST_COUNT,
            4,
        )

    error_rate = 0
    if config.CHAT_REQUEST_COUNT > 0:
        error_rate = round(
            config.CHAT_ERROR_COUNT / config.CHAT_REQUEST_COUNT,
            4,
        )

    avg_response_length = 0
    if config.CHAT_SUCCESS_COUNT > 0:
        avg_response_length = int(
            config.TOTAL_RESPONSE_CHARS / config.CHAT_SUCCESS_COUNT
        )

    p95_processing_ms = compute_p95(config.PROCESSING_TIMES)
    openai_latency_p95 = compute_p95(config.OPENAI_LATENCIES)

    now = time.time()
    window_start = now - 60

    requests_last_60s = len(
        [ts for ts in config.REQUEST_TIMESTAMPS if ts >= window_start]
    )

    process = psutil.Process(os.getpid())

    engine_memory_mb = round(
        process.memory_info().rss / 1024 / 1024,
        2,
    )

    engine_cpu_percent = round(
        process.cpu_percent(interval=None),
        2,
    )

    engine_threads = threading.active_count()

    return {
        "engine": config.ENGINE_NAME,
        "version": config.ENGINE_VERSION,
        "build_version": config.BUILD_VERSION,
        "model": config.OPENAI_MODEL,
        "engine_instance_id": config.ENGINE_INSTANCE_ID,
        "engine_started_at": config.ENGINE_STARTED_AT,
        "uptime_seconds": uptime,
        "chat_requests_total": config.CHAT_REQUEST_COUNT,
        "chat_success_total": config.CHAT_SUCCESS_COUNT,
        "chat_errors_total": config.CHAT_ERROR_COUNT,
        "avg_processing_ms": avg_processing_ms,
        "max_processing_ms": config.MAX_PROCESSING_MS,
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
        "rate_limit_per_minute": config.RATE_LIMIT_PER_MINUTE,
        "openai_status": config.OPENAI_STATUS,
    }
