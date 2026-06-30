from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Conversation
from .serializers import (
ConversationSerializer,
ConversationDetailSerializer,
SendMessageSerializer,
)

from .services.chat_service import send_message_stream
from lexi.common.responses import success_response

class ConversationListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        conversations = (
            Conversation.objects
            .filter(user=request.user)
            .order_by("-updated_at")
        )

        serializer = ConversationSerializer(
            conversations,
            many=True
        )

        return success_response(
            message="تم جلب المحادثات بنجاح.",
            data=serializer.data
        )

    def post(self, request):

        conversation = Conversation.objects.create(
            user=request.user
        )

        serializer = ConversationSerializer(
            conversation
        )

        return success_response(
            message="تم إنشاء المحادثة بنجاح.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

class ConversationDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user
        )

        serializer = ConversationDetailSerializer(
            conversation
        )

        return success_response(
            message="تم جلب المحادثة بنجاح.",
            data=serializer.data
        )

    def delete(self, request, conversation_id):

        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user
        )

        conversation.delete()

        return success_response(
            message="تم حذف المحادثة بنجاح."
        )


# class SendMessageView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(
#         self,
#         request,
#         conversation_id
#     ):

#         serializer = SendMessageSerializer(
#             data=request.data
#         )

#         serializer.is_valid(
#             raise_exception=True
#         )

#         conversation = get_object_or_404(
#             Conversation,
#             id=conversation_id,
#             user=request.user
#         )

#         question = serializer.validated_data[
#             "question"
#         ]

#         answer = send_message(
#             conversation,
#             question
#         )

#         return success_response(
#             message="تم إرسال الرسالة بنجاح.",
#             data={
#                 "answer": answer
#             }
#         )

from django.http import StreamingHttpResponse
import json

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user
        )

        question = serializer.validated_data["question"]

        def event_stream():
            try:
                for chunk in send_message_stream(conversation, question):
                    yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"

                yield f"data: {json.dumps({'done': True})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
        )
