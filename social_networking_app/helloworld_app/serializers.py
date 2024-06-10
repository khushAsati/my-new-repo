# your_app/serializers.py
from rest_framework import serializers
from .models import FriendRequest, User

class UserSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    address = serializers.CharField()

    def create(self, validated_data):
        user = User(**validated_data)
        user.save()
        return user
class FriendRequestSerializer(serializers.Serializer):
    from_user = UserSerializer()
    to_user = UserSerializer()
    class Meta:
        model = FriendRequest
        ffields = '__all__'

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)