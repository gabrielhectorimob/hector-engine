from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from typing import Any, Dict

app = FastAPI(title="Hector Engine", version="1.0.0")

# Memória temporária do modelo carregado pelo Excel
HECTOR_STATE: Dict[str, Any] = {
    "model": {},
    "loaded": False
}


class Question(BaseModel):
    question: str


class HectorModelPayload(BaseModel):
    model: Dict[str, Any]


@app.get("/")
def root():
    return {"message": "Hector Engine running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": HECTOR_STATE["loaded"],
        "tabs_loaded": list(HECTOR_STATE["model"].keys()) if HECTOR_STATE["loaded"] else []
    }


@app.post("/upload-model")
def upload_model(payload: HectorModelPayload):
    HECTOR_STATE["model"] = payload.model
    HECTOR_STATE["loaded"] = True

    summary = {}
    for sheet_name, rows in payload.model.items():
        if isinstance(rows, list):
            summary[sheet_name] = len(rows)
        else:
            summary[sheet_name] = 0

    return {
        "status": "model_loaded",
        "tabs_received": list(payload.model.keys()),
        "rows_per_tab": summary
    }


@app.post("/query")
def query(q: Question):
    if not HECTOR_STATE["loaded"]:
        return {
            "answer": "O modelo Hector ainda não foi carregado. Execute primeiro o exportador do Excel."
        }

    tabs = list(HECTOR_STATE["model"].keys())
    brain_rows = len(HECTOR_STATE["model"].get("HECTOR_BRAIN", []))
    context_rows = len(HECTOR_STATE["model"].get("HECTOR_CONTEXT", []))
    benchmark_rows = len(HECTOR_STATE["model"].get("HECTOR_BENCHMARK", []))

    return {
        "answer": (
            f"Hector recebeu a pergunta: {q.question}. "
            f"Modelo carregado com {len(tabs)} abas HECTOR_. "
            f"HECTOR_BRAIN: {brain_rows} linhas. "
            f"HECTOR_CONTEXT: {context_rows} linhas. "
            f"HECTOR_BENCHMARK: {benchmark_rows} linhas."
        )
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
