from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import traceback
import os

# =========================================
# APP
# =========================================

app = FastAPI()

# =========================================
# MODELO DE REQUISIÇÃO
# =========================================

class Query(BaseModel):
    question: str

# =========================================
# ROOT
# =========================================

@app.get("/")
def root():
    return {"engine": "hector running"}

# =========================================
# FUNÇÃO DE BUSCA (TEMPORÁRIA PARA TESTE)
# =========================================

def run_query(question: str):

    # aqui você depois conecta:
    # rag.search
    # embeddings
    # openai
    # qdrant

    return f"Pergunta recebida: {question}"

# =========================================
# ENDPOINT QUERY
# =========================================

@app.post("/query")
async def query(q: Query):

    print("=================================")
    print("QUESTION RECEIVED:", q.question)
    print("=================================")

    try:

        result = run_query(q.question)

        print("RESULT:", result)

        return {
            "answer": result
        }

    except Exception as e:

        print("ERROR OCCURRED")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
