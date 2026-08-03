# account/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import datetime
import secrets
import pytz
from account.models import User
from account.utils import (
    hash_password,
    verify_password,
    create_token,
    decode_token
)

# Helper function to convert UTC to IST
def utc_to_ist(utc_dt):
    """Convert UTC datetime to IST timezone"""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
    ist = pytz.timezone('Asia/Kolkata')
    return utc_dt.astimezone(ist)

def format_ist_datetime(dt):
    """Format datetime in IST for display"""
    if dt:
        ist_dt = utc_to_ist(dt)
        return ist_dt.strftime('%Y-%m-%d %I:%M:%S %p %Z')  # e.g., 2026-08-02 05:10:44 PM IST
    return None

def get_user_response(user):
    """Helper to format user response with IST time"""
    return {
        "id": str(user.id),
        "fname": user.fname,
        "lname": user.lname,
        "email": user.email,
        "created_at": format_ist_datetime(user.created_at)
    }


@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid JSON data"
        }, status=400)

    # Validate required fields
    required_fields = ["fname", "lname", "email", "password"]
    for field in required_fields:
        if field not in body or not body[field]:
            return JsonResponse({
                "success": False,
                "message": f"{field} is required"
            }, status=400)

    # Check if email already exists
    if User.objects(email=body["email"]).first():
        return JsonResponse({
            "success": False,
            "message": "Email already exists."
        }, status=400)

    # Create user with UTC time
    user = User(
        fname=body["fname"],
        lname=body["lname"],
        email=body["email"],
        password=hash_password(body["password"]),
        created_at=datetime.datetime.utcnow()
    )
    user.save()

    # Create token
    token = create_token(user)

    return JsonResponse({
        "success": True,
        "message": "Registration successful!",
        "token": token,
        "user": get_user_response(user)  # Returns IST formatted time
    })


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid JSON data"
        }, status=400)

    # Validate required fields
    if "email" not in body or not body["email"]:
        return JsonResponse({
            "success": False,
            "message": "Email is required"
        }, status=400)

    if "password" not in body or not body["password"]:
        return JsonResponse({
            "success": False,
            "message": "Password is required"
        }, status=400)

    # Find user
    user = User.objects(email=body["email"]).first()

    if not user:
        return JsonResponse({
            "success": False,
            "message": "Invalid Email or Password"
        }, status=401)

    # Verify password
    if not verify_password(body["password"], user.password):
        return JsonResponse({
            "success": False,
            "message": "Invalid Email or Password"
        }, status=401)

    # Create token
    token = create_token(user)

    return JsonResponse({
        "success": True,
        "message": "Login successful!",
        "token": token,
        "user": get_user_response(user)  # Returns IST formatted time
    })


@csrf_exempt
@require_http_methods(["POST"])
def google_login_callback(request):
    """
    Handle Google OAuth callback and return JWT tokens.
    This is called from frontend after receiving Google ID token.
    """
    try:
        body = json.loads(request.body)
        email = body.get('email')
        fname = body.get('first_name', '')
        lname = body.get('last_name', '')
        google_id = body.get('google_id')
        picture = body.get('picture', '')
        
        if not email:
            return JsonResponse({
                "success": False, 
                "message": "Email is required"
            }, status=400)
        
        # Check if user exists
        user = User.objects(email=email).first()
        
        if not user:
            # Create new user with random password
            random_password = secrets.token_urlsafe(20)
            
            user = User(
                fname=fname or "Google",
                lname=lname or "User",
                email=email,
                password=hash_password(random_password),
                created_at=datetime.datetime.utcnow()
            )
            user.save()
        
        # Generate JWT token
        token = create_token(user)
        
        return JsonResponse({
            "success": True,
            "message": "Google login successful!",
            "token": token,
            "user": get_user_response(user)  # Returns IST formatted time
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid JSON data"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Google login failed: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_user_profile(request):
    """
    Get user profile with IST formatted time.
    Requires authentication token in header.
    """
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                "success": False,
                "message": "Authentication required"
            }, status=401)
        
        token = auth_header.split(' ')[1]
        
        # Decode token to get user info
        from account.utils import decode_token
        payload = decode_token(token)
        
        if not payload:
            return JsonResponse({
                "success": False,
                "message": "Invalid or expired token"
            }, status=401)
        
        # Find user
        user = User.objects(id=payload.get('id')).first()
        
        if not user:
            return JsonResponse({
                "success": False,
                "message": "User not found"
            }, status=404)
        
        return JsonResponse({
            "success": True,
            "user": get_user_response(user)  # Returns IST formatted time
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Error: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def update_profile_view(request):
    """Update user profile"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                "success": False,
                "message": "Authentication required"
            }, status=401)
        
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        
        if not payload:
            return JsonResponse({
                "success": False,
                "message": "Invalid or expired token"
            }, status=401)
        
        user = User.objects(id=payload.get('id')).first()
        
        if not user:
            return JsonResponse({
                "success": False,
                "message": "User not found"
            }, status=404)
        
        body = json.loads(request.body)
        
        # Update fields
        if 'fname' in body and body['fname']:
            user.fname = body['fname']
        if 'lname' in body and body['lname']:
            user.lname = body['lname']
        if 'email' in body and body['email']:
            # Check if email is already taken by another user
            existing_user = User.objects(email=body['email']).first()
            if existing_user and str(existing_user.id) != str(user.id):
                return JsonResponse({
                    "success": False,
                    "message": "Email already taken"
                }, status=400)
            user.email = body['email']
        
        user.save()
        
        return JsonResponse({
            "success": True,
            "message": "Profile updated successfully!",
            "user": get_user_response(user)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid JSON data"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Error: {str(e)}"
        }, status=500)