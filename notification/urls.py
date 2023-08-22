from django.urls import path
from .views import SendEmailView

urlpatterns = [
    path('send_email/', SendEmailView.as_view(), name='send_email'),
]