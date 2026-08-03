from rest_framework import serializers # type: ignore
from django.contrib.auth.models import User


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
            "password"
        ]

    def create(self, validated_data):

        user = User.objects.create_user(

            username=validated_data["username"],

            email=validated_data["email"],

            password=validated_data["password"],

            first_name=validated_data["first_name"],

            last_name=validated_data["last_name"]
        )

        return user