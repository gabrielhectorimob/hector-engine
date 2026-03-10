from fastapi import FastAPI
import os
import httpx

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/responses"


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/debug-env")
def debug_env():
    if not OPENAI_API_KEY:
        return {
            "success": False,
            "error": "OPENAI_API_KEY not found"
        }

    return {
        "success": True,
        "key_prefix": OPENAI_API_KEY[:7]
    }


@app.get("/debug-openai-http")
def debug_openai_http():
    if not OPENAI_API_KEY:
        return {
            "success": False,
            "error": "OPENAI_API_KEY not found"
        }

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
            response = client.post(OPENAI_URL, headers=headers, json=payload)

        return {
            "success": response.is_success,
            "status_code": response.status_code,
            "body": response.json()
        }

    except Exception as e:
        return {
            "success": False,
            "error_type": type(e).__name__,
            "error": str(e)
        }
