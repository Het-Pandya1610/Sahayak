from mongoengine import (Document,StringField,EmailField,DateTimeField) # type: ignore

from datetime import datetime


class User(Document):

    fname = StringField(
        required=True
    )

    lname = StringField(
        required=True
    )

    email = EmailField(
        required=True,
        unique=True
    )

    password = StringField(
        required=True
    )

    created_at = DateTimeField(
        default=datetime.utcnow
    )