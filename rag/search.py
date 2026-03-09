from qdrant_client import QdrantClient
from rag.embeddings import create_embedding
import os

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION = "hector_knowledge"

def search(query):

    vector = create_embedding(query)

    results = client.search(
        collection_name=COLLECTION,
        query_vector=vector,
        limit=5
    )

    return [r.payload for r in results]
