from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import traceback

app = FastAPI()

client = OpenAI()

class Query(BaseModel):
    question: str

@app.get("/")
def root():
    return {"engine": "hector running"}

def run_query(question: str):

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Você é o Hector, especialista em loteamentos."},
            {"role": "user", "content": question}
        ]
    )

    return response.choices[0].message.content

@app.post("/query")
async def query(q: Query):

    try:

        answer = run_query(q.question)

        return {
            "answer": answer
        }

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
