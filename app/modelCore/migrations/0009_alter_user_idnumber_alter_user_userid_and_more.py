# Generated by Django 4.0.4 on 2022-05-13 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0008_user_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='idNumber',
            field=models.CharField(default='', max_length=20, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='userId',
            field=models.CharField(default='', max_length=10, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='vehicalLicence',
            field=models.CharField(default='', max_length=255, null=True, unique=True),
        ),
    ]
