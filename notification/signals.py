from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from surveys.models import Survey

User = get_user_model()

@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
    if created and instance.is_sleeping:
        # 최초 생성 시, 이메일 인증(verification)
        with get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS
        ) as connection:

            verification_link = f'http://127.0.0.1:8000/user/verify/{instance.pk}'
            email = EmailMessage(
                subject='Email Verification for Your Account',
                body=f'Please click the link below to verify your email address:\n\n{verification_link}',
                from_email=settings.EMAIL_HOST_USER,
                to=[instance.email],
                connection=connection)
            email.send()

@receiver(post_save, sender=User)
def send_register_email(sender, instance, created, **kwargs):
    if not instance.is_sleeping:
        # 이메일 인증 이후 환영 메시지
        with get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS
        ) as connection:

            email = EmailMessage(
                subject='Welcome to Data Quest Pro!',
                body=f'Welcome, {instance.name}!\n\nThank you for your regesteration.',
                from_email=settings.EMAIL_HOST_USER,
                to=[instance.email],
                connection=connection)
            email.send()


@receiver(post_save, sender=Survey)
def survey_create_email(sender, instance, created, **kwargs):
    if created:
        with get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS
        ) as connection:

            email = EmailMessage(
                subject='title',
                body='body',
                from_email=settings.EMAIL_HOST_USER,
                to=[instance.user.email],
                connection=connection)
            email.send()


@receiver(pre_save, sender=Survey)
def survey_close_email(sender, instance, **kwargs):
    if instance.is_done:
        print(sender.objects.get(id=instance.id).is_done)
        print(instance.is_done)
        with get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS
        ) as connection:

            useranswers = instance.useranswer_set.all()
            targets = set()
            for useranswer in useranswers:
                if useranswer.user.email_opt_in:
                    targets.add(useranswer.user.email)
                else:
                    continue
            email = EmailMessage(
                subject=instance.title + 'is done',
                body='zz',
                from_email=settings.EMAIL_HOST_USER,
                to=list(targets),
                connection=connection)
            email.send()
