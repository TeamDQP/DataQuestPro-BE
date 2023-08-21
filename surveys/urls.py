from django.urls import path
from .views import SurveyCreate, SurveyDetail, SurveyDelete, CategoryCreate, TagCreate

app_name = 'surveys'

urlpatterns = [
    ### survey
    path('survey/create/', SurveyCreate.as_view(), name='survey-create'),
    path('survey/detail/<int:pk>', SurveyDetail.as_view(), name='survey-detail'),
    path('survey/delete/<int:pk>', SurveyDelete.as_view(), name='survey-delete'),

    ### category
    path('category/create/', CategoryCreate.as_view(), name='category-create'),

    ### tag
    path('tag/create/', TagCreate.as_view(), name='Tag-create'),
]