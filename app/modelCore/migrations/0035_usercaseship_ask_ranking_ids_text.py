# Generated by Django 4.1.5 on 2023-04-06 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0034_remove_usercaseship_ask_ranking_ids_text_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercaseship',
            name='ask_ranking_ids_text',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
