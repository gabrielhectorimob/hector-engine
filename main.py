from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.system import router as system_router

app = FastAPI(
    title="Hector Engine",
    version="1.0"
)

app.include_router(system_router)
app.include_router(chat_router)
