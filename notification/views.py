from django.views import View
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.shortcuts import render
from django.http import HttpResponse


class SendEmailView(View):
    def post(self, request):
        with get_connection(
            host=settings.EMAIL_HOST, 
            port=settings.EMAIL_PORT,  
            username=settings.EMAIL_HOST_USER, 
            password=settings.EMAIL_HOST_PASSWORD, 
            use_tls=settings.EMAIL_USE_TLS  
            ) as connection:
            subject = request.POST.get("subject")  
            email_from = settings.EMAIL_HOST_USER  
            recipient_list = [request.POST.get("email"), ]  
            message = request.POST.get("message")  
            EmailMessage(subject, message, email_from, recipient_list, connection=connection).send()
    
    # def get(self, request, *args, **kwargs):
    #     subject = "message"
    #     to = ["odh0112@naver.com"]
    #     from_email = "odh0112@naver.com"
    #     message = "메세지 테스트"
    #     email = EmailMessage(subject=subject, body=message, to=to, from_email=from_email)
    #     email.send()
    #     return HttpResponse("Email sent successfully")
