from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, ProfileSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .models import Profile
from django.contrib.auth import get_user_model
User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class JWTValidationView(APIView):
    # The user is authenticated,
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # # the token is valid
            token = AccessToken(request.META.get(
                'HTTP_AUTHORIZATION').split(' ')[-1])
            return Response('Token Validated', status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class EmailVerification(APIView):
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if user.is_sleeping:
                user.is_sleeping = False
                user.save()
                return Response('wake', status=status.HTTP_200_OK)
            return Response('Email has already been verified.', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)


class UserUpdate(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(email=request.user)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = User.objects.get(email=request.user)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDelete(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = User.objects.get(email=request.user)
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_404_NOT_FOUND)


class ProfileWrite(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # user = request.data.get('user')
        # image = request.data.get('image')
        # username = request.data.get('username')
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileRead(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileUpdate(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            # print(request.data)
            # print(serializer.validated_data['profileimage'])
            # print(type(serializer.validated_data['profileimage']))
            if serializer.validated_data['profileimage']:
                serializer.save()
            else:
                # print('null')
                serializer.save(profileimage=profile.profileimage)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDelete(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):  # request 안에 user가 있으므로 pk가 필요없음.
        profile = Profile.objects.get(user=request.user)
        profile.delete()
        return Response(status=status.HTTP_404_NOT_FOUND)
