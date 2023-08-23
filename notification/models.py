from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailManager(models.Manager):
    def f(self):
        pass

# https://docs.djangoproject.com/en/4.2/topics/email/
class EmailRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)    # 요청보내는 유저
    title = models.CharField(max_length=255)    # 이메일 제목
    body = models.TextField()   # 본문 내용
    targets = models.TextField()    # 수신인 목록을 공백으로 구분하여 문자열로 저장(리스트에서 .join하여 저장)
    # 이메일 송신 목적
    PURPOSE_TYPES = [
        ('register', 'Register'),   # 회원가입
    ]
    purpose = models.CharField(max_length=10, choices=PURPOSE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_done = models.BooleanField(default=False)
    
    objects = EmailManager()