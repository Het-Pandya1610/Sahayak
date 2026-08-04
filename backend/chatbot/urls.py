from django.urls import path
from .views import (
    chatbot_response,  # Keep the original endpoint
    chat_session_list,
    chat_session_detail,
    chat_session_create,
    chat_session_delete,
    chat_message_send,
    chat_session_rename,
    chat_clear_messages,
    chat_delete_message,
    chat_edit_message,
    analyze_image,
    send_email,
)

urlpatterns = [
    # Original chatbot endpoint (keep this)
    path('ask/', chatbot_response, name='chatbot_response'),
    
    # Session management
    path('sessions/', chat_session_list, name='chat_sessions'),
    path('sessions/create/', chat_session_create, name='chat_session_create'),
    path('sessions/<str:session_id>/', chat_session_detail, name='chat_session_detail'),
    path('sessions/<str:session_id>/delete/', chat_session_delete, name='chat_session_delete'),
    path('sessions/<str:session_id>/rename/', chat_session_rename, name='chat_session_rename'),

    # Messages
    path('sessions/<str:session_id>/send/', chat_message_send, name='chat_message_send'),

    #Message management
    path('sessions/<str:session_id>/clear/', chat_clear_messages, name='chat_clear_messages'),
    path('sessions/<str:session_id>/messages/<str:message_id>/delete/', chat_delete_message, name='chat_delete_message'),
    path('sessions/<str:session_id>/messages/<str:message_id>/edit/', chat_edit_message, name='chat_edit_message'),
    
    path('analyze-image/', analyze_image, name='analyze_image'),
    path('send-email/', send_email, name='send_email'),
]