import bcrypt
import jwt
import datetime
from django.conf import settings

def hash_password(password):
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(
        password.encode(),
        hashed.encode()
    )

def create_token(user):
    payload = {
        "id": str(user.id),
        "email": user.email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256"
    )

def decode_token(token):
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
    except:
        return None