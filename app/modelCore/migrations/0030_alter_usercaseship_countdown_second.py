# Generated by Django 4.1.5 on 2023-03-06 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0029_usercaseship_expect_second'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercaseship',
            name='countdown_second',
            field=models.IntegerField(default=16),
        ),
    ]