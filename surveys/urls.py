from django.urls import path
from .views import SurveyCreate, SurveyDetail, SurveyUpdate, SurveyDelete, SurveyResult, IndexMain, UserAnswerView

app_name = 'surveys'

urlpatterns = [
    ### survey
    path('survey/', IndexMain.as_view(), name='survey'),
    path('survey/create/', SurveyCreate.as_view(), name='survey-create'),

    path('survey/update/<int:pk>', SurveyUpdate.as_view(), name='survey-update'),

    path('survey/detail/<int:pk>', SurveyDetail.as_view(), name='survey-detail'),
    path('survey/delete/<int:pk>', SurveyDelete.as_view(), name='survey-delete'),
    path('survey/submit/', UserAnswerView.as_view(), name='survey-submit'),
    path('survey/result/<int:pk>', SurveyResult.as_view(), name='survey-result'),
]