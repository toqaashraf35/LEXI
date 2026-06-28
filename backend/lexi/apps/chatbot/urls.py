from django.urls import path

from .views import (
    ConversationListCreateView,
    ConversationDetailView,
    SendMessageView,
)

urlpatterns = [
    path("conversations/", ConversationListCreateView.as_view(), name="conversation-list-create"),
    path("conversations/<int:conversation_id>/", ConversationDetailView.as_view(), name="conversation-detail"),
    path("conversations/<int:conversation_id>/messages/", SendMessageView.as_view(), name="send-message"),
]