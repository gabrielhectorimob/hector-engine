from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
import traceback

app = FastAPI()

# ===============================
# OPENAI CONFIG
# ===============================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY environment variable not found")

client = OpenAI(api_key=OPENAI_API_KEY)

# ===============================
# MODELS
# ===============================
class Query(BaseModel):
    question: str

# ===============================
# ROUTES
# ===============================
@app.get("/")
def root():
    return {"engine": "hector running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query")
def query(data: Query):
    try:

        response = client.chat.completions.create(
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

        answer = response.choices[0].message.content

        return {
            "answer": answer
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
