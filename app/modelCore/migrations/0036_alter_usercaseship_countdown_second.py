# Generated by Django 4.1.5 on 2023-04-06 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0035_usercaseship_ask_ranking_ids_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercaseship',
            name='countdown_second',
            field=models.IntegerField(default=18),
        ),
    ]
