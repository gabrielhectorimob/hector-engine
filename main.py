import os
from fastapi import FastAPI, Request
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# =====================================
# CONFIGURAÇÕES
# =====================================

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

COLLECTION_NAME = "hector_brain"

# =====================================
# CLIENTES
# =====================================

openai_client = OpenAI(api_key=OPENAI_API_KEY)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# =====================================
# APP
# =====================================

app = FastAPI()

# =====================================
# CRIAR COLLECTION SE NÃO EXISTIR
# =====================================

def garantir_collection():

    collections = qdrant.get_collections().collections
    nomes = [c.name for c in collections]

    if COLLECTION_NAME not in nomes:

        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=3072,
                distance=Distance.COSINE
            )
        )

garantir_collection()

# =====================================
# GERAR EMBEDDING
# =====================================

def gerar_embedding(texto):

    response = openai_client.embeddings.create(
        model="text-embedding-3-large",
        input=texto
    )

    return response.data[0].embedding


# =====================================
# INDEXAÇÃO
# =====================================

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

# =====================================
# BUSCA
# =====================================

@app.post("/hector/buscar")
async def buscar(request: Request):

    body = await request.json()

    pergunta = body["pergunta"]

    embedding = gerar_embedding(pergunta)

    resultados = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=5
    )

    dados = []

    for r in resultados:
        dados.append(r.payload)

    return {
        "contexto": dados
    }

# =====================================
# STATUS
# =====================================

@app.get("/")
def status():

    return {
        "status": "HECTOR ENGINE ONLINE",
        "vector_db": "Qdrant",
        "embeddings": "OpenAI"
    }
