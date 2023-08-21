from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)


class Survey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    intro = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_done = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Tag(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    qnum = models.IntegerField()
    QUESTION_TYPES = [
        ('scale', 'Scale'),
        ('open', 'Open-ended'),
    ]
    type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=False)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    point = models.IntegerField(null=True, blank=True)  # '척도형 점수'
    body = models.TextField(null=True, blank=True)     # '서술형 응답'
