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


@app.get("/health")
def health():

    return {
        "server": "ok",
        "openai_key_loaded": bool(OPENAI_API_KEY)
    }


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

    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(OPENAI_URL, headers=headers, json=payload)

        data = r.json()

        resposta = ""

        if "output" in data:
            try:
                resposta = data["output"][0]["content"][0]["text"]
            except:
                resposta = str(data)
        else:
            resposta = str(data)

        return {
            "resposta": resposta
        }

    except Exception as e:

        return {
            "erro": str(e)
        }
