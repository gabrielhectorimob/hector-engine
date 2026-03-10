from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
import traceback

app = FastAPI()

# =========================
# OPENAI CONFIG
# =========================
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
    raise Exception("OPENAI_API_KEY not configured")

client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# MODELO
# =========================
class Query(BaseModel):
    question: str

# =========================
# ROTAS
# =========================
@app.get("/")
def root():
    return {"engine": "hector running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query")
def query(data: Query):

    try:

        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é o Hector, especialista em loteamentos e análise imobiliária."
                },
                {
                    "role": "user",
                    "content": data.question
                }
            ]
        )

        return {
            "answer": completion.choices[0].message.content
        }

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
