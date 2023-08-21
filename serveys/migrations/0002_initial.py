# Generated by Django 4.2.4 on 2023-08-20 06:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('serveys', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='serveys.survey'),
        ),
        migrations.AddField(
            model_name='category',
            name='survey',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='serveys.survey'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='serveys.question'),
        ),
    ]
