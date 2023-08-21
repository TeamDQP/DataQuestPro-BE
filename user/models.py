from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

# Create your models here.


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('User must have an email')
        # now = timezone.now() # 현재시간을 받아옴. -> UTC로 가져옴
        now = timezone.localtime()
        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)

# 하나씩 수정이 필요한 attribute를 생성해줌.


class User(AbstractUser):
    username = None
    # unique=True 를 통해 primary key 로 만들어줌.
    email = models.EmailField(unique=True, max_length=255)
    # null=True 는 데이터베이스에 넣을때 값이 null 이어도 됨. blank=True 값이 비어있어도 됨
    name = models.CharField(max_length=50, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # username을 email로 해주겠다.
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    # 슈퍼유저 생성할때 어떤것을 받을건지 알려주는 것.
    REQUIRED_FIELDS = []

    # 우리가 만든 아래의 클래스를 helper로 사용하겠다.
    objects = UserManager()


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    profileimage = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
