from django.contrib import admin
from .models import Survey, Category, Tag, Question, Answer, UserAnswer

# Register your models here.
admin.site.register(Survey) # admin 페이지에 등록
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(UserAnswer)