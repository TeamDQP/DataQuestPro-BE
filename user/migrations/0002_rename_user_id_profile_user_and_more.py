# Generated by Django 4.2.4 on 2023-08-22 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='user_id',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='profile',
            name='profileimage',
            field=models.ImageField(upload_to='user/media'),
        ),
    ]