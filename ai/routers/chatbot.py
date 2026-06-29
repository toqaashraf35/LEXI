# from fastapi import APIRouter

# from schemas.chatbot import (
#     ChatRequest,
#     ChatResponse,
# )

# from services.chatbot_service import generate_answer

# router = APIRouter(
#     prefix="/chatbot",
#     tags=["Chatbot"],
# )


# @router.post(
#     "/chat",
#     response_model=ChatResponse,
# )
# def chat(request: ChatRequest):

#     answer = generate_answer(
#         request.question,
#         request.history,
#     )

#     return ChatResponse(
#         answer=answer
#     )

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json

from schemas.chatbot import ChatRequest
from services.chatbot_service import generate_answer

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


@router.post("/chat")
def chat(request: ChatRequest):

    def event_stream():
        for chunk in generate_answer(request.question, request.history):
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )