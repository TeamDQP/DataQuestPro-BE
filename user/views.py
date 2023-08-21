
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


# Create your views here.
class RegisterView(FormView):
    template_name = '#템플릿'
    form_class = RegisterForm
    # 로그인 성공시 리다이렉트 url
    success_url = '/home'

    def form_valid(self, form):
        # 회원가입 폼이 유효한 경우, 사용자 생성 및 저장
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        # Django의 내장 User 모델을 사용하여 사용자 생성
        user = User.objects.create_user(username=email, email=email, password=password)
        login(self.request, user)
        return super().form_valid(form)


class LogoutView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
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

