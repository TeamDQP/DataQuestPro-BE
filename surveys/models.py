from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)


class Tag(models.Model):
    name = models.CharField(max_length=255)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)


class Survey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    intro = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_done = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', related_name='surveys')
    views = models.IntegerField(default=0)


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    qnum = models.IntegerField()
    QUESTION_TYPES = [
        ('scale', 'Scale'),
        ('open', 'Open-ended'),
    ]
    type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=False)
    question_text = models.TextField()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_point = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    answer_text = models.TextField(blank=True)
