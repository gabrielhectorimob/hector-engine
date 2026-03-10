from fastapi import FastAPI
from pydantic import BaseModel
import traceback

# módulos do projeto
from parser.excel_parser import parse_excel
from rag.embeddings import create_embedding
from rag.search import search_documents

from vector_search import vector_search


app = FastAPI(title="Hector Engine")


# -----------------------------
# MODELO DE PERGUNTA
# -----------------------------

class Query(BaseModel):
    question: str
    context: str | None = None


# -----------------------------
# ENDPOINT ROOT
# -----------------------------

@app.get("/")
def root():
    return {"engine": "hector", "status": "running"}


# -----------------------------
# HEALTH CHECK
# -----------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# CONSULTA PRINCIPAL
# -----------------------------

@app.post("/query")
def query(q: Query):

    try:

        question = q.question

        # embedding da pergunta
        embedding = create_embedding(question)

        # busca vetorial
        results = vector_search(embedding)

        # busca RAG complementar
        rag_results = search_documents(question)

        return {
            "question": question,
            "vector_results": results,
            "rag_results": rag_results
        }

    except Exception as e:

        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }
