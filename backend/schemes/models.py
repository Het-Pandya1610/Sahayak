from mongoengine import (Document,StringField,ListField,BooleanField)  # type: ignore

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

    extracted_categories = ListField(StringField())  # e.g., ['sc', 'st', 'general']
    is_category_specific = BooleanField(default=False)  # True if scheme mentions any category
    eligible_categories = ListField(StringField())  # Standardized category names
    primary_category = StringField()

    meta = {
        'collection': 'schemes',
        'indexes': [
            'scheme_name',
            'slug',
            'level',
            'schemeCategory',
            'tags',
            'extracted_categories',
            'eligible_categories',
            'primary_category',
        ]
    }
