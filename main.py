from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# cria cliente OpenAI usando variável de ambiente
client = OpenAI()


class Query(BaseModel):
    question: str


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/query")
def run_query(data: Query):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é o Hector, especialista em loteamentos."
                },
                {
                    "role": "user",
                    "content": data.question
                }
            ]
        )

        return {
            "response": response.choices[0].message.content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
