from rest_framework import serializers
from .models import User, Profile


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["email", "name", "password", "email_opt_in"]

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"], name=validated_data["name"], email_opt_in=validated_data["email_opt_in"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["username", "profileimage"]
