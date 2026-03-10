from fastapi import FastAPI
from openai import OpenAI
import httpx
import certifi
import os

app = FastAPI()

# pega API key do Railway
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# cliente OpenAI
client = OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=httpx.Client(
        verify=certifi.where(),
        timeout=30.0
    )
)

@app.get("/")
def root():
    return {"status": "Hector Engine running"}

@app.get("/test-openai")
def test_openai():

    if not OPENAI_API_KEY:
        return {
            "success": False,
            "error": "OPENAI_API_KEY not found"
        }

    try:

        response = client.responses.create(
            model="gpt-4.1-mini",
            input="Responda apenas OK"
        )

        return {
            "success": True,
            "response": response.output_text
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }
