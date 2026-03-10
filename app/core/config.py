import os
import time
import uuid
from datetime import datetime, timezone

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
