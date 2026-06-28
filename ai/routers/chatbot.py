from fastapi import APIRouter

from schemas.chatbot import (
    ChatRequest,
    ChatResponse,
)

from services.chatbot_service import generate_answer

router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"],
)


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    answer = generate_answer(
        request.question,
        request.history,
    )

    return ChatResponse(
        answer=answer
    )