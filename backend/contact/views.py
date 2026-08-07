from django.core.mail import EmailMessage
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from account.models import User
import json
from account.utils import decode_token


@csrf_exempt
@require_http_methods(["POST"])
def send_contact_email(request):
    """
    Send a contact form message to the Sahayak team.
    User email is fetched from the authenticated user's database record.
    """

    try:
        # -----------------------------------------
        # 1. Get token from Authorization header
        # -----------------------------------------
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                "success": False,
                "message": "Authentication required"
            }, status=401)

        token = auth_header.split(' ')[1]

        # -----------------------------------------
        # 2. Decode JWT
        # -----------------------------------------
        payload = decode_token(token)

        if not payload:
            return JsonResponse({
                "success": False,
                "message": "Invalid or expired token"
            }, status=401)

        # -----------------------------------------
        # 3. Find authenticated user
        # -----------------------------------------
        user = User.objects(id=payload.get('id')).first()

        if not user:
            return JsonResponse({
                "success": False,
                "message": "User not found"
            }, status=404)

        # -----------------------------------------
        # 4. Get email directly from database
        # -----------------------------------------
        user_email = user.email

        if not user_email:
            return JsonResponse({
                "success": False,
                "message": "No email address found for this account"
            }, status=400)

        # -----------------------------------------
        # 5. Get form data
        # -----------------------------------------
        name = request.POST.get('name', '').strip()
        message = request.POST.get('message', '').strip()

        # If frontend sends JSON
        if request.content_type == 'application/json':
            import json

            data = json.loads(request.body)

            name = data.get('name', '').strip()
            message = data.get('message', '').strip()

        # -----------------------------------------
        # 6. Validate form data
        # -----------------------------------------
        if not name:
            return JsonResponse({
                "success": False,
                "message": "Name is required"
            }, status=400)

        if not message:
            return JsonResponse({
                "success": False,
                "message": "Message is required"
            }, status=400)

        # -----------------------------------------
        # 7. Create email
        # -----------------------------------------
        subject = f"Sahayak Contact Form - Message from {name}"

        email_body = f"""
You have received a new message through the Sahayak Contact Us form.

Name: {name}
Email: {user_email}

Message:
{message}
"""

        # -----------------------------------------
        # 8. Send email
        # -----------------------------------------
        email_message = EmailMessage(
            subject=subject,
            body=email_body,
            from_email='Sahayak Contact Form <teamsahayak3@gmail.com>',
            to=['teamsahayak3@gmail.com'],
            reply_to=[user_email],
        )

        email_message.send(fail_silently=False)

        # -----------------------------------------
        # 9. Success response
        # -----------------------------------------
        return JsonResponse({
            "success": True,
            "message": "Your message has been sent successfully."
        })

    except Exception as e:

        print("Contact email error:", e)

        return JsonResponse({
            "success": False,
            "message": "Failed to send your message. Please try again later."
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def report_misinformation(request):

    try:

        # Get JWT token
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                "success": False,
                "message": "Authentication required"
            }, status=401)


        token = auth_header.split(' ')[1]


        # Decode token
        payload = decode_token(token)

        if not payload:
            return JsonResponse({
                "success": False,
                "message": "Invalid token"
            }, status=401)



        # Get user
        user = User.objects(
            id=payload.get('id')
        ).first()


        if not user:
            return JsonResponse({
                "success": False,
                "message": "User not found"
            }, status=404)



        user_email = user.email



        # Get JSON data
        data = json.loads(request.body)

        url = data.get('url', '').strip()
        description = data.get('description', '').strip()



        if not url or not description:
            return JsonResponse({
                "success": False,
                "message": "URL and description are required"
            }, status=400)



        subject = "Sahayak Misinformation Report"


        body = f"""
A new misinformation report has been submitted.

Reporter:
{user_email}


URL:
{url}


Description:
{description}

"""


        email = EmailMessage(

            subject=subject,

            body=body,

            from_email='Sahayak Reports <teamsahayak3@gmail.com>',

            to=[
                'teamsahayak3@gmail.com'
            ],

            reply_to=[
                user_email
            ]
        )


        email.send(
            fail_silently=False
        )


        return JsonResponse({

            "success": True,

            "message": "Report submitted successfully"

        })



    except Exception as e:

        print(e)

        return JsonResponse({

            "success": False,

            "message": str(e)

        }, status=500)