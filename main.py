import os
from fastapi import FastAPI, Request
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# ==========================================
# CONFIGURAÇÕES
# ==========================================

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

COLLECTION_NAME = "hector_brain"

# ==========================================
# CLIENTES
# ==========================================

openai_client = OpenAI(api_key=OPENAI_API_KEY)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# ==========================================
# APP
# ==========================================

app = FastAPI()

# ==========================================
# FUNÇÃO GERAR EMBEDDING
# ==========================================

def gerar_embedding(texto):

    response = openai_client.embeddings.create(
        model="text-embedding-3-large",
        input=texto
    )

    return response.data[0].embedding


# ==========================================
# INDEXAÇÃO
# ==========================================

@app.post("/hector/indexar")
async def indexar_documentos(request: Request):

    dados = await request.json()

    points = []

    for i, doc in enumerate(dados):

        texto = doc["texto"]

        embedding = gerar_embedding(texto)

        points.append(
            PointStruct(
                id=i,
                vector=embedding,
                payload=doc
            )
        )

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return {
        "status": "indexado",
        "total_documentos": len(points)
    }


# ==========================================
# BUSCA SEMÂNTICA
# ==========================================

@app.post("/hector/buscar")
async def buscar_contexto(request: Request):

    body = await request.json()

    pergunta = body["pergunta"]

    embedding = gerar_embedding(pergunta)

    search = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=5
    )

    resultados = []

    for r in search:
        resultados.append(r.payload)

    return {
        "contexto": resultados
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
def status():

    return {
        "status": "HECTOR ENGINE ONLINE",
        "vector_db": "Qdrant",
        "embeddings": "OpenAI"
    }
