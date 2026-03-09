import os
from fastapi import FastAPI
from openai import OpenAI

# pegar API key do ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set")

# criar cliente
client = OpenAI(api_key=OPENAI_API_KEY)

# criar app
app = FastAPI()


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/ask")
def ask_ai(question: str):
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": question}
        ]
    )

    return {
        "response": response.choices[0].message.content
    }
