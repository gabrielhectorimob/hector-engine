from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
import traceback

app = FastAPI()

# =========================
# OPENAI CONFIG
# =========================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# MODELO DE ENTRADA
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

        print("Pergunta recebida:", data.question)

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é o Hector, especialista em loteamentos imobiliários."
                },
                {
                    "role": "user",
                    "content": data.question
                }
            ]
        )

        answer = response.choices[0].message.content

        print("Resposta gerada:", answer)

        return {
            "answer": answer
        }

    except Exception as e:

        print("ERRO REAL:")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
