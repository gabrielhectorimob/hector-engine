import os
import threading
import time
import uuid
from datetime import datetime, timezone


def build_request_context() -> dict:
    return {
        "request_id": str(uuid.uuid4()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "process_time_reference": time.time(),
        "thread_count": threading.active_count(),
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "local"),
    }
