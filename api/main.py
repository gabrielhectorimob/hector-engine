from fastapi import FastAPI
from openai import OpenAI
import os

from rag.search import search

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def root():
    return {"status": "HECTOR ENGINE ONLINE"}

@app.get("/chat")
def chat(msg: str):

    context = search(msg)

    prompt = f"""
    Você é Hector, especialista em loteamentos.

    Contexto:
    {context}

    Pergunta:
    {msg}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )

    return {
        "response": response.choices[0].message.content
    }
