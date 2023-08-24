from django.urls import path
from .views import SurveyCreate, SurveyDetail, SurveyDelete, CategoryCreate, TagCreate, IndexMain, UserAnswerView

app_name = 'surveys'

urlpatterns = [
    ### survey
    path('survey/', IndexMain.as_view(), name='survey'),
    path('survey/create/', SurveyCreate.as_view(), name='survey-create'),
    path('survey/detail/<int:pk>', SurveyDetail.as_view(), name='survey-detail'),
    path('survey/delete/<int:pk>', SurveyDelete.as_view(), name='survey-delete'),

    path('survey/submit/', UserAnswerView.as_view(), name='survey-submit'),

    ### category
    path('category/create/', CategoryCreate.as_view(), name='category-create'),

    ### tag
    path('tag/create/', TagCreate.as_view(), name='Tag-create'),
]