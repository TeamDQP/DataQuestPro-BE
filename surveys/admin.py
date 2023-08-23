from django.contrib import admin
from .models import Survey, Category, Tag, Question, AnswerOption, UserAnswer

# Register your models here.
admin.site.register(Survey) # admin 페이지에 등록
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(AnswerOption)
admin.site.register(UserAnswer)