# Generated by Django 4.1.7 on 2023-02-20 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0022_case_telegram_id_user_telegram_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='nick_name',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]
