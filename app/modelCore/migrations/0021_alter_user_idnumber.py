# Generated by Django 4.1.5 on 2023-02-15 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0020_carteam_remove_case_userid_remove_user_car_model_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='idNumber',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
    ]