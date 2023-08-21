from django.urls import path
from .views import Survey_Create, Category_Create, Tag_Create

app_name = 'surveys'

urlpatterns = [
    path('survey/create/', Survey_Create.as_view(), name='survey-create'),
    path('category/create/', Category_Create.as_view(), name='category-create'),
    path('tag/create/', Tag_Create.as_view(), name='Tag-create'),
]