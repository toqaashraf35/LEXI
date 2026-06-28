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


def generate_ai_response(question, history):

    response = requests.post(
        f"{settings.AI_SERVICE_URL}/chatbot/chat",
        json={
            "question": question,
            "history": history
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["answer"]


def send_message(conversation, question):

    history = get_history(conversation)

    Message.objects.create(
        conversation=conversation,
        role="user",
        content=question
    )

    ai_response = generate_ai_response(
        question,
        history
    )

    Message.objects.create(
        conversation=conversation,
        role="assistant",
        content=ai_response
    )

    if not conversation.title:
        conversation.title = generate_title(question)
        conversation.save()

    return ai_response