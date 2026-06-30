import json
from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):

    content = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "role",
            "content",
            "created_at"
        ]

    def get_content(self, obj):

        if obj.role == "assistant":
            try:
                return json.loads(obj.content)
            except Exception:
                return obj.content

        return obj.content


class ConversationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "created_at",
            "updated_at"
        ]


class ConversationDetailSerializer(serializers.ModelSerializer):

    messages = MessageSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "created_at",
            "updated_at",
            "messages"
        ]


class SendMessageSerializer(serializers.Serializer):

    question = serializers.CharField(
    allow_blank=True,
    error_messages={
        "required": "الرسالة مطلوبة.",
    }
)

    def validate_question(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "لا يمكن إرسال رسالة فارغة."
            )

        return value