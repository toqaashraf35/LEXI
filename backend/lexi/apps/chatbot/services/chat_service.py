import requests

from django.conf import settings
from ..models import Conversation, Message


def get_history(conversation):

    messages = conversation.messages.order_by("created_at")

    history = []

    for message in messages:
        history.append(
            {
                "role": message.role,
                "content": message.content
            }
        )

    return history


def generate_title(question):
    return question[:50]

import json

def generate_ai_response_stream(question, history):
    with requests.post(
        f"{settings.AI_SERVICE_URL}/chatbot/chat",
        json={"question": question, "history": history},
        stream=True,
        timeout=120,
    ) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            if line and line.startswith(b"data: "):
                data = json.loads(line[6:])
                if data.get("done"):
                    return
                if data.get("chunk"):
                    yield data["chunk"]


def send_message_stream(conversation, question):
    history = get_history(conversation)

    Message.objects.create(
        conversation=conversation,
        role="user",
        content=question
    )

    full_answer = ""

    for chunk in generate_ai_response_stream(question, history):
        full_answer += chunk
        yield chunk

    Message.objects.create(
        conversation=conversation,
        role="assistant",
        content=full_answer
    )

    if not conversation.title:
        conversation.title = generate_title(question)
        conversation.save()