# Generated by Django 4.0.4 on 2022-07-10 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0012_alter_case_case_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='create_time',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
