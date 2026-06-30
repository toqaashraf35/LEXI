from typing import List
from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: List[Message] = []


class ChatResponse(BaseModel):
    answer: str