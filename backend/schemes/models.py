from mongoengine import (Document,StringField,ListField)  # type: ignore

class Scheme(Document):

    scheme_name = StringField(required=True)

    slug = StringField()

    details = StringField()

    benefits = StringField()

    eligibility = StringField()

    application = StringField()

    documents = StringField()

    level = StringField()

    schemeCategory = StringField()

    tags = ListField(StringField())

    meta = {
        'collection': 'schemes',
        'indexes': [
            'scheme_name',
            'slug',
            'level',
            'schemeCategory',
            'tags'
        ]
    }
