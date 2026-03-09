from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Any

app = FastAPI()

# memória global do modelo
model_memory: Dict[str, List[Dict[str, Any]]] = {}

# ------------------------------
# MODELOS
# ------------------------------

class Question(BaseModel):
    question: str

class ModelUpload(BaseModel):
    model: Dict[str, List[Dict[str, Any]]]


# ------------------------------
# STATUS
# ------------------------------

@app.get("/")
def root():
    return {"message": "Hector Engine running"}

@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------------
# UPLOAD DO MODELO
# ------------------------------

@app.post("/upload-model")
def upload_model(data: ModelUpload):

    global model_memory

    model_memory = data.model

    rows_per_tab = {}

    for tab, rows in model_memory.items():
        rows_per_tab[tab] = len(rows)

    return {
        "status": "model_loaded",
        "tabs_received": list(model_memory.keys()),
        "rows_per_tab": rows_per_tab
    }


# ------------------------------
# DEBUG MODELO COMPLETO
# ------------------------------

@app.get("/debug-model")
def debug_model():

    return {
        "tabs": list(model_memory.keys()),
        "data": model_memory
    }


# ------------------------------
# AMOSTRA DOS DADOS
# ------------------------------

@app.get("/model-sample")
def model_sample():

    sample = {}

    for tab, rows in model_memory.items():
        sample[tab] = rows[:5]

    return sample


# ------------------------------
# AUDITORIA DO MODELO
# ------------------------------

@app.get("/model-audit")
def model_audit():

    audit = {}

    total_rows = 0
    empty_fields = 0
    units_detected = set()
    domains_detected = set()

    for tab, rows in model_memory.items():

        audit[tab] = len(rows)
        total_rows += len(rows)

        for row in rows:

            if "UNIDADE" in row and row["UNIDADE"]:
                units_detected.add(row["UNIDADE"])

            if "DOMINIO" in row and row["DOMINIO"]:
                domains_detected.add(row["DOMINIO"])

            for value in row.values():
                if value == "" or value is None:
                    empty_fields += 1

    return {
        "tabs": len(model_memory),
        "rows_total": total_rows,
        "rows_per_tab": audit,
        "empty_fields": empty_fields,
        "units_detected": list(units_detected),
        "domains_detected": list(domains_detected)
    }


# ------------------------------
# QUERY (PERGUNTAS)
# ------------------------------

@app.post("/query")
def query(q: Question):

    return {
        "answer": f"Hector recebeu a pergunta: {q.question}",
        "model_tabs_loaded": list(model_memory.keys())
    }
