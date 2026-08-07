from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from datetime import datetime
from account.utils import decode_token
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatSessionListSerializer

# Import your existing chatbot pipeline
from chatbot.ai.chatbot_engine.pipeline import chatbot_pipeline

from .deep_learning import ImageProcessor, EmailGenerator
import base64
from io import BytesIO
from PIL import Image

image_processor = ImageProcessor()
email_generator = EmailGenerator()

def get_user_from_token(request):
    """Extract user ID from JWT token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    payload = decode_token(token)
    if not payload:
        return None
    
    return payload.get('id')

# ============================================================
# ORIGINAL CHATBOT ENDPOINT (Keep this for backward compatibility)
# ============================================================
@csrf_exempt
def chatbot_response(request):
    """Original chatbot endpoint - keep this working"""
    if request.method != 'POST':
        return JsonResponse({
            'error': 'POST request required'
        }, status=400)

    try:
        body = json.loads(request.body)
        query = body.get('query', '')
        
        if not query:
            return JsonResponse({
                'error': 'Query is required'
            }, status=400)

        history = body.get('history', [])
        response = chatbot_pipeline(query, history)

        return JsonResponse(response, safe=False)

    except Exception as e:
        print("CHATBOT ERROR:", str(e))
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================================

@csrf_exempt
def chat_session_list(request):
    """Get all chat sessions for a user"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user_id = get_user_from_token(request)
    if not user_id:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        sessions = ChatSession.objects(user_id=user_id, is_active=True).order_by('-updated_at')
        serializer = ChatSessionListSerializer(sessions, many=True)
        
        return JsonResponse({
            'success': True,
            'sessions': serializer.data
        })
    except Exception as e:
        print("Error in chat_session_list:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def chat_session_detail(request, session_id):
    """Get a specific chat session with all messages"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user_id = get_user_from_token(request)
    if not user_id:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        session = ChatSession.objects.get(id=uuid.UUID(session_id), user_id=user_id, is_active=True)
        serializer = ChatSessionSerializer(session)
        return JsonResponse({
            'success': True,
            'session': serializer.data
        })
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid session ID'}, status=400)
    except Exception as e:
        print("Error in chat_session_detail:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def chat_session_create(request):
    """Create a new chat session"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user_id = get_user_from_token(request)
    if not user_id:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        body = json.loads(request.body)
        title = body.get('title', 'New Chat')
        
        session = ChatSession(
            user_id=user_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.save()
        
        # Add welcome message
        welcome_msg = ChatMessage(
            session=session,
            role='assistant',
            content="Hello! I'm your trusted AI guide. Ask me about any government scheme — I'll provide accurate, verified details.",
            created_at=datetime.utcnow()
        )
        welcome_msg.save()
        
        serializer = ChatSessionSerializer(session)
        return JsonResponse({
            'success': True,
            'session': serializer.data
        })
    except Exception as e:
        print("Error in chat_session_create:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def chat_session_delete(request, session_id):
    """Delete a chat session and all its messages (hard delete)"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user_id = get_user_from_token(request)
    if not user_id:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        # Find the session
        session = ChatSession.objects.get(id=uuid.UUID(session_id), user_id=user_id)
        
        # Get session info for response
        session_title = session.title
        
        # Delete the session (this will cascade delete all messages)
        session.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Chat session "{session_title}" deleted successfully',
            'deleted': True
        })
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid session ID'}, status=400)
    except Exception as e:
        print("Error deleting session:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def chat_message_send(request, session_id):
    """Send a message or image in a chat session"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user_id = get_user_from_token(request)
    if not user_id:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        session = ChatSession.objects.get(id=uuid.UUID(session_id), user_id=user_id, is_active=True)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid session ID'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    try:
        body = json.loads(request.body)
        query = body.get('query', '')
        image_data = body.get('image', None)
        location = body.get('location', '')
        user_prompt = body.get('prompt', '')
        
        # Check if this is an image analysis request
        if image_data:
            # Process image
            print("📸 Processing image from chat...")
            prediction = image_processor.predict(image_data)
            print(f"Prediction: {prediction}")
            
            # Extract features for severity assessment
            features = image_processor.extract_features(image_data)
            severity_score = image_processor.assess_severity(prediction, features)
            prediction['severity'] = severity_score
            
            # Get user data from token
            user_data = {
                'name': 'Citizen',
                'contact': 'N/A',
                'email': 'N/A'
            }
            
            # Generate email
            email_data = email_generator.generate_email(
                prediction_result=prediction,
                user_data=user_data,
                location=location or 'Unknown Location',
                custom_prompt=user_prompt or query
            )
            
            # Save user message (the prompt or query)
            user_message = ChatMessage(
                session=session,
                role='user',
                content=query or f"Analyze this image: {location}",
                created_at=datetime.utcnow()
            )
            user_message.save()
            
            # Save assistant message with image analysis result
            assistant_response = f"""📸 **Image Analysis Result**

**Issue Type:** {email_data['issue_type'].replace('_', ' ').upper()}
**Confidence:** {(prediction.get('confidence', 0) * 100):.1f}%
**Severity:** {email_data['severity']}
**Location:** {location or 'Unknown'}

**Generated Email:**
{email_data['body']}

**Subject:** {email_data['subject']}

Would you like me to send this email? (Reply with 'yes' to send)"""
            
            assistant_message = ChatMessage(
                session=session,
                role='assistant',
                content=assistant_response,
                schemes=[],  # No schemes, it's an image analysis
                created_at=datetime.utcnow()
            )
            assistant_message.save()
            
            # Store email data in session for later use
            # We'll save it in a temporary field or you can create a new model
            session.title = f"Image Analysis: {email_data['issue_type']}"
            session.updated_at = datetime.utcnow()
            session.save()
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': str(assistant_message.id),
                    'role': assistant_message.role,
                    'content': assistant_message.content,
                    'schemes': [],
                    'is_image_analysis': True,
                    'email_data': email_data,
                    'prediction': prediction
                }
            })
        
        # Regular text message flow
        if not query:
            return JsonResponse({'error': 'Query is required'}, status=400)
        
        # Save user message
        user_message = ChatMessage(
            session=session,
            role='user',
            content=query,
            created_at=datetime.utcnow()
        )
        user_message.save()
        
        # Get chat history for context
        history = []
        for msg in ChatMessage.objects(session=session).order_by('created_at'):
            history.append({
                'role': msg.role,
                'content': msg.content
            })
        
        # Call chatbot pipeline
        response = chatbot_pipeline(query, history, session_id=session_id)
        
        # Save assistant message
        assistant_message = ChatMessage(
            session=session,
            role='assistant',
            content=response.get('answer', 'No response generated'),
            schemes=response.get('schemes', []),
            created_at=datetime.utcnow()
        )
        assistant_message.save()
        
        # Update session title if it's the first user message
        user_count = ChatMessage.objects(session=session, role='user').count()
        if user_count == 1:
            session.title = query[:50] + ('...' if len(query) > 50 else '')
            session.save()
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        session.save()
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': str(assistant_message.id),
                'role': assistant_message.role,
                'content': assistant_message.content,
                'schemes': assistant_message.schemes,
                'created_at': assistant_message.created_at.isoformat(),
                'is_image_analysis': False
            }
        })
        
    except Exception as e:
        print("Error in chat_message_send:", str(e))
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def chat_session_rename(request, session_id):
    """Rename a chat session"""
    if request.method != 'PATCH':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user_id = get_user_from_token(request)
    if not user_id:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        session = ChatSession.objects.get(id=uuid.UUID(session_id), user_id=user_id, is_active=True)
        
        body = json.loads(request.body)
        new_title = body.get('title', '').strip()
        
        if not new_title:
            return JsonResponse({'error': 'Title is required'}, status=400)
        
        session.title = new_title
        session.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Session renamed successfully',
            'session': {
                'id': str(session.id),
                'title': session.title,
                'updated_at': session.updated_at.isoformat()
            }
        })
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid session ID'}, status=400)
    except Exception as e:
        print("Error renaming session:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def chat_clear_messages(request, session_id):
    """Clear all messages in a chat session (keep only welcome message)"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user_id = get_user_from_token(request)
    if not user_id:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        session = ChatSession.objects.get(id=uuid.UUID(session_id), user_id=user_id, is_active=True)
        
        # Delete all messages except the welcome message
        # Get the welcome message (first message in the session)
        first_msg = ChatMessage.objects(session=session).order_by('created_at').first()
        
        # Delete all messages
        ChatMessage.objects(session=session).delete()
        
        # Re-create welcome message
        welcome_msg = ChatMessage(
            session=session,
            role='assistant',
            content="Hello! I'm your trusted AI guide. Ask me about any government scheme — I'll provide accurate, verified details.",
            created_at=datetime.utcnow()
        )
        welcome_msg.save()
        
        # Update session title
        session.title = "New Chat"
        session.updated_at = datetime.utcnow()
        session.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Chat cleared successfully',
            'session': {
                'id': str(session.id),
                'title': session.title
            }
        })
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid session ID'}, status=400)
    except Exception as e:
        print("Error clearing chat:", str(e))
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def chat_delete_message(request, session_id, message_id):
    """Delete a specific message and its paired response"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user_id = get_user_from_token(request)
    if not user_id:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        session = ChatSession.objects.get(id=uuid.UUID(session_id), user_id=user_id, is_active=True)
        
        # Find the message to delete
        try:
            message = ChatMessage.objects.get(id=uuid.UUID(message_id), session=session)
        except ChatMessage.DoesNotExist:
            return JsonResponse({'error': 'Message not found'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Invalid message ID'}, status=400)
        
        # Get the message role and timestamp
        message_role = message.role
        message_created = message.created_at
        
        # Delete the message
        message.delete()
        
        # If it was a user message, also delete the assistant's response (if any)
        deleted_paired = False
        if message_role == 'user':
            # Find the assistant message that came after this user message
            paired_msg = ChatMessage.objects(
                session=session,
                role='assistant',
                created_at__gt=message_created
            ).order_by('created_at').first()
            
            if paired_msg:
                paired_msg.delete()
                deleted_paired = True
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        session.save()
        
        # Check if this was the last user message, update title
        user_count = ChatMessage.objects(session=session, role='user').count()
        if user_count == 0:
            session.title = "New Chat"
            session.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Message deleted successfully',
            'paired_deleted': deleted_paired
        })
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid ID'}, status=400)
    except Exception as e:
        print("Error deleting message:", str(e))
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def chat_edit_message(request, session_id, message_id):
    """Edit a user message and regenerate response"""
    if request.method != 'PUT':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user_id = get_user_from_token(request)
    if not user_id:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        body = json.loads(request.body)
        new_content = body.get('content', '')
        
        if not new_content:
            return JsonResponse({'error': 'New content is required'}, status=400)
        
        session = ChatSession.objects.get(id=uuid.UUID(session_id), user_id=user_id, is_active=True)
        
        # Find the user message
        user_message = ChatMessage.objects.get(id=uuid.UUID(message_id), session=session)
        
        if user_message.role != 'user':
            return JsonResponse({'error': 'Only user messages can be edited'}, status=400)
        
        # Delete the associated assistant response if it exists
        next_messages = ChatMessage.objects(session=session, created_at__gt=user_message.created_at).order_by('created_at')
        if next_messages.count() > 0:
            next_msg = next_messages.first()
            if next_msg.role == 'assistant':
                next_msg.delete()
        
        # Update the user message
        user_message.content = new_content
        user_message.created_at = datetime.utcnow()  # Update timestamp
        user_message.save()
        
        # Get full chat history for context
        history = []
        for msg in ChatMessage.objects(session=session).order_by('created_at'):
            history.append({
                'role': msg.role,
                'content': msg.content
            })
        
        # Call chatbot pipeline to generate new response
        response = chatbot_pipeline(new_content, history)
        
        # Save new assistant message
        assistant_message = ChatMessage(
            session=session,
            role='assistant',
            content=response.get('answer', 'No response generated'),
            schemes=response.get('schemes', []),
            created_at=datetime.utcnow()
        )
        assistant_message.save()
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        session.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Message edited and response regenerated',
            'user_message': {
                'id': str(user_message.id),
                'content': user_message.content,
                'created_at': user_message.created_at.isoformat()
            },
            'assistant_message': {
                'id': str(assistant_message.id),
                'content': assistant_message.content,
                'schemes': assistant_message.schemes,
                'created_at': assistant_message.created_at.isoformat()
            }
        })
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except ChatMessage.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid ID'}, status=400)
    except Exception as e:
        print("Error editing message:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def analyze_image(request):
    """
    Analyze an image and generate a professional email
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    try:
        body = json.loads(request.body)
        
        # Get image data
        image_data = body.get('image')
        location = body.get('location', 'Unknown Location')
        user_prompt = body.get('prompt', '')
        user_data = body.get('user', {})
        
        if not image_data:
            return JsonResponse({'error': 'Image data is required'}, status=400)
        
        if not location:
            return JsonResponse({'error': 'Location is required'}, status=400)
        
        # Process the image
        print("Analyzing image...")
        prediction = image_processor.predict(image_data)
        print(f"Prediction: {prediction}")
        
        # Extract features for severity assessment
        features = image_processor.extract_features(image_data)
        
        # Assess severity
        severity_score = image_processor.assess_severity(prediction, features)
        prediction['severity'] = severity_score
        
        # Generate email
        email_data = email_generator.generate_email(
            prediction_result=prediction,
            user_data=user_data,
            location=location,
            custom_prompt=user_prompt
        )
        
        response = email_generator.generate_response(email_data)
        
        return JsonResponse(response)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        print("Image analysis error:", str(e))
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def send_email(request):
    """
    Send the generated email (mock implementation)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    try:
        body = json.loads(request.body)
        email_data = body.get('email', {})
        recipient = body.get('recipient', 'municipalcorporation@example.com')
        
        if not email_data:
            return JsonResponse({'error': 'Email data is required'}, status=400)
        
        # In a real implementation, this would send an actual email
        # For now, we'll just log it and return success
        
        print(f"Email sent to: {recipient}")
        print(f"Subject: {email_data.get('subject')}")
        print(f"Body: {email_data.get('body')[:200]}...")
        
        return JsonResponse({
            'success': True,
            'message': 'Email sent successfully!',
            'recipient': recipient,
            'sent_at': datetime.now().isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)