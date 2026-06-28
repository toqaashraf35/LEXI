from fastapi import FastAPI
from routers.chatbot import router as chatbot_router

app = FastAPI(
    title="LEXI AI",
    version="1.0.0",
)

app.include_router(chatbot_router)