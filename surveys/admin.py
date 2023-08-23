from django.contrib import admin
from .models import Survey, Category, Tag, Question, Answer


# Register your models here.
admin.site.register(Category)
admin.site.register(Survey)
admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Answer)
