from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from .serializers import EmailRecordSerializer
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .email_templates import purposes


class SendEmailView(APIView):    
    def post(self, request):
        permission_classes = (IsAuthenticated,)
        email_serializer = EmailRecordSerializer(data=request.data)
        if email_serializer.is_valid():
            with get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS
                ) as connection:
                purpose = request.data.get('purpose')
                # title = request.data.get('title')   # 이메일 제목
                title = purposes[purpose][title]
                # body = request.data.get('body')   # 본문 내용
                body = purposes[purpose][body]
                recipient_list = request.data.get('targets').split()    # 수신인 목록(list or tuple)
                from_email = settings.EMAIL_HOST_NAME + '<' + settings.EMAIL_HOST_USER + '>'    # "Fred" <fred@example.com>
                try:
                    if EmailMessage(subject=title, body=body, to=recipient_list, from_email=from_email, connection=connection).\
                    send(fail_silently=True):
                        return Response(email_serializer.data, status=status.HTTP_200_OK)
                    return Response({"message":"recipient_list trouble: empty list or the targets data cannot be split"})
                except Exception as e:
                    return Response({"message":"maybe a connection error"})
        return Response(email_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 테스트용 get 코드
    def get(self, request):
        permission_classes = (IsAuthenticated,)
        
        try:
            title = "환영합니다."
            body = "Body: 본문 내용 테스트"
            recipient_list = [request.user.email]
            from_email = settings.EMAIL_HOST_NAME + '<' + settings.EMAIL_HOST_USER + '>'    # "Fred" <fred@example.com>
            # EmailMessage(subject=title, body=body, to=recipient_list, from_email=from_email).send()
            text_content = "This is an important message."
            html_content = "<p>This is an <strong>important</strong> message.</p>"
            html_content = render_to_string('welcome_email.html', body)  # welcome_email.html은 이메일 내용을 담은 HTML 템플릿입니다.
            text_content = strip_tags(html_content)  # HTML 태그를 제거한 텍스트 버전
            msg = EmailMultiAlternatives(subject=title, body=body, to=recipient_list, from_email=from_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return Response({"result":"Email sent successfully"})
        except Exception as e:
            return Response({"result":e})
