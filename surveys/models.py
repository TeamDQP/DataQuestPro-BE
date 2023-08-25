from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Survey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    intro = models.TextField() # 설문조사 설명
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # enddated_at 추가
    is_done = models.BooleanField(default=False) # 설문 조사 종료 체크
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)# 설문조사 유형
    tags = models.ManyToManyField('Tag', related_name='surveys', null=True, blank=True) # 제작자의 태그
    views = models.IntegerField(default=0)


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    qnum = models.IntegerField() # 질문순서
    QUESTION_TYPES = [
        ('scale', 'Scale'),
        ('open', 'Open-ended'),
    ]
    type = models.CharField(max_length=10, choices=QUESTION_TYPES) # 객관식, 서술형
    is_required = models.BooleanField(default=False) # 필수인지 아닌지
    question_text = models.TextField() # 질문 텍스트


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField() # 답변 예제


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)


class UserAnswerDetail(models.Model):
    useranswer_id = models.ForeignKey(UserAnswer, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_point = models.ForeignKey(AnswerOption, on_delete=models.CASCADE, null=True, blank=True) # 객관식답변
    answer_text = models.TextField(null=True, blank=True) # 서술형답변