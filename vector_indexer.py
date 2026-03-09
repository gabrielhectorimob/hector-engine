import os
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# ===============================
# CONFIGURAÇÕES
# ===============================

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

COLLECTION_NAME = "hector_brain"

# ===============================
# CLIENTES
# ===============================

openai_client = OpenAI(api_key=OPENAI_API_KEY)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# ===============================
# GERAR EMBEDDING
# ===============================

def gerar_embedding(texto):

    response = openai_client.embeddings.create(
        model="text-embedding-3-large",
        input=texto
    )

    return response.data[0].embedding


# ===============================
# INDEXAR DOCUMENTOS
# ===============================

def indexar_documentos(documentos):

    points = []

    for i, doc in enumerate(documentos):

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

    return {"status": "indexado", "total": len(points)}
