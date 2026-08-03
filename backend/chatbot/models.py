from mongoengine import Document, StringField, ListField, DictField, DateTimeField, ReferenceField, BooleanField, UUIDField
from datetime import datetime
import uuid

class ChatSession(Document):
    """Chat session model for storing conversations in MongoDB"""
    id = UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    user_id = StringField(required=True, max_length=255)
    title = StringField(max_length=255, default="New Chat")
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    is_active = BooleanField(default=True)
    
    meta = {
        'collection': 'chat_sessions',
        'indexes': [
            'user_id',
            '-updated_at',
            ('user_id', '-updated_at'),
        ],
        'ordering': ['-updated_at']
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Delete all messages when session is deleted"""
        # Delete all messages associated with this session
        ChatMessage.objects(session=self).delete()
        return super().delete(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.user_id}"

class ChatMessage(Document):
    """Chat message model for storing individual messages in MongoDB"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    session = ReferenceField('ChatSession', required=True, reverse_delete_rule=2)  # CASCADE
    role = StringField(max_length=10, choices=ROLE_CHOICES, default='user')
    content = StringField(required=True)
    schemes = ListField(DictField(), default=list)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'chat_messages',
        'indexes': [
            'session',
            'created_at',
            ('session', 'created_at'),
        ],
        'ordering': ['created_at']
    }
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."