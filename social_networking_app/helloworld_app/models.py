from mongoengine import Document, StringField,fields
from django.db import models
from mongoengine import Document, ReferenceField, DateTimeField, BooleanField, CASCADE
from django.contrib.auth import get_user_model
from datetime import datetime


    # Add more fields as needed

class User(Document):
    name = fields.StringField(max_length=100, required=True)
    email = fields.EmailField(unique=True, required=True)
    password = fields.StringField(max_length=100, required=True)
    address = fields.StringField(required=True)

    def __str__(self):
        return self.email


class FriendRequest(Document):
    from_user = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    to_user = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    timestamp = DateTimeField(default=datetime.utcnow)
    accepted = BooleanField(default=False)

    meta = {
        'indexes': [
            {'fields': ('from_user', 'to_user'), 'unique': True}
        ]
    }