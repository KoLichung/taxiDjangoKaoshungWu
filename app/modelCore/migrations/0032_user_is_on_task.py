# Generated by Django 4.1.5 on 2023-03-10 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0031_user_is_telegram_bot_enable'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_on_task',
            field=models.BooleanField(default=False),
        ),
    ]