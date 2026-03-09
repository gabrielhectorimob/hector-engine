from qdrant_client import QdrantClient
from rag.embeddings import create_embedding
import os

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION = "hector_knowledge"

def index_document(text, metadata):

    embedding = create_embedding(text)

    client.upsert(
        collection_name=COLLECTION,
        points=[
            {
                "id": hash(text),
                "vector": embedding,
                "payload": metadata
            }
        ]
    )
