from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Profile


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        # fields = ["email", "name", "password"]
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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_active:
            raise Exception
        if self.user.is_sleeping:
            raise Exception
        return data
