import os
from openai import OpenAI
from qdrant_client import QdrantClient

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

COLLECTION_NAME = "hector_brain"

openai_client = OpenAI(api_key=OPENAI_API_KEY)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)


def gerar_embedding(texto):

    response = openai_client.embeddings.create(
        model="text-embedding-3-large",
        input=texto
    )

    return response.data[0].embedding


def buscar_contexto(pergunta):

    embedding = gerar_embedding(pergunta)

    search = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=5
    )

    resultados = []

    for r in search:
        resultados.append(r.payload)

    return resultados
