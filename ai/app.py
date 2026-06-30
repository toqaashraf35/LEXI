from fastapi import FastAPI
from routers.chatbot import router as chatbot_router
from routers.contract_analysis import router as contract_analysis_router
from routers.training import router as training_router

app = FastAPI(
    title="LEXI AI",
    version="1.0.0",
)

app.include_router(chatbot_router)
app.include_router(contract_analysis_router)
app.include_router(training_router)