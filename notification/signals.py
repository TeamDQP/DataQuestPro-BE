from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from surveys.models import Survey

User = get_user_model()


@receiver(post_save, sender=User)
def send_register_email(sender, instance, created, **kwargs):
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
    print(sender.objects.get(id=instance.id).is_done)
    print(instance.is_done)
    if instance.is_done:
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
                targets.add(useranswer.user.email)

            email = EmailMessage(
                subject='title',
                body='body',
                from_email=settings.EMAIL_HOST_USER,
                to=list(targets),
                connection=connection)
            email.send()
