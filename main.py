from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import os

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION = "hector"


class Query(BaseModel):
    question: str


@app.get("/")
def root():
    return {"engine": "hector running"}


@app.post("/query")
def query(q: Query):

    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=q.question
    ).data[0].embedding

    results = qdrant.search(
        collection_name=COLLECTION,
        query_vector=embedding,
        limit=3
    )

    context = "\n".join([r.payload["text"] for r in results])

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Responda baseado no contexto."},
            {"role": "user", "content": f"Contexto:\n{context}\n\nPergunta:{q.question}"}
        ]
    )

    return {
        "answer": completion.choices[0].message.content
    }
