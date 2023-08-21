from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login

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

