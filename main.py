from fastapi import FastAPI
from pydantic import BaseModel
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


class ChatRequest(BaseModel):
    pergunta: str


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/chat")
def chat(req: ChatRequest):

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4.1-mini",
        "input": req.pergunta
    }

    with httpx.Client(timeout=30.0) as client:
        r = client.post(OPENAI_URL, headers=headers, json=payload)

    return r.json()
