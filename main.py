from fastapi import FastAPI
import os
import httpx

app = FastAPI()

RAW_KEY = os.getenv("OPENAI_API_KEY", "")

OPENAI_API_KEY = (
    RAW_KEY
    .replace("\n", "")
    .replace("\r", "")
    .strip()
)

OPENAI_URL = "https://api.openai.com/v1/responses"


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/debug-env")
def debug_env():
    return {
        "raw_length": len(RAW_KEY),
        "clean_length": len(OPENAI_API_KEY),
        "key_prefix": OPENAI_API_KEY[:7]
    }


@app.get("/debug-openai-http")
def debug_openai_http():

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4.1-mini",
        "input": "Responda apenas OK"
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(OPENAI_URL, headers=headers, json=payload)

        return {
            "success": r.is_success,
            "status_code": r.status_code,
            "body": r.json()
        }

    except Exception as e:
        return {
            "success": False,
            "error_type": type(e).__name__,
            "error": str(e)
        }
