from rest_framework import serializers # type: ignore
from .models import ChatSession, ChatMessage
import json

class ChatMessageSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    role = serializers.CharField()
    content = serializers.CharField()
    schemes = serializers.ListField(default=list)
    created_at = serializers.DateTimeField()

class ChatSessionSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    is_active = serializers.BooleanField()
    messages = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    def get_messages(self, obj):
        """Get messages for this session using MongoEngine query"""
        messages = ChatMessage.objects(session=obj).order_by('created_at')
        return ChatMessageSerializer(messages, many=True).data
    
    def get_message_count(self, obj):
        """Get message count for this session"""
        return ChatMessage.objects(session=obj).count()

class ChatSessionListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ')
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ')
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    def get_message_count(self, obj):
        """Get message count for this session"""
        return ChatMessage.objects(session=obj).count()
    
    def get_last_message(self, obj):
        """Get last message for this session"""
        last_msg = ChatMessage.objects(session=obj).order_by('-created_at').first()
        if last_msg:
            return last_msg.content[:100]
        return None