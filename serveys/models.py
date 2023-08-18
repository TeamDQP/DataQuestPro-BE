from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class Survey(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    intro = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_done = models.BooleanField(default=False)


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    survey = models.OneToOneField(Survey, on_delete=models.CASCADE)


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    tag = models.CharField(max_length=255)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    qnum = models.IntegerField()
    type = models.CharField(max_length=255)  # '척도형/서술형'
    is_required = models.BooleanField(default=False)


class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    point = models.IntegerField(null=True, blank=True)  # '척도형 점수'
    body = models.TextField(null=True, blank=True)     # '서술형 응답'
