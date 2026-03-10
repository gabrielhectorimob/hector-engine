from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Pergunta enviada pelo usuário")


class ChatResponse(BaseModel):
    request_id: str
    engine: str
    answer: str
    brain: dict
