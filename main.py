from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

app = FastAPI()

class Question(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "Hector Engine running"}

@app.post("/query")
def query(q: Question):
    return {
        "answer": f"Hector recebeu a pergunta: {q.question}"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
