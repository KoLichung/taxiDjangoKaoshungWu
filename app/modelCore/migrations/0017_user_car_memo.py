# Generated by Django 4.1.5 on 2023-01-11 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0016_remove_monthsummary_month_decrease_money_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='car_memo',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
