from pydantic import BaseModel


class ChatRequest(BaseModel):
    pergunta: str
