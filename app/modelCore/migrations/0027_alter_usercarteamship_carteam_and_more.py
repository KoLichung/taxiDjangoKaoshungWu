# Generated by Django 4.1.5 on 2023-02-21 02:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0026_merge_20230221_0943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercarteamship',
            name='carTeam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='car_team_users', to='modelCore.carteam'),
        ),
        migrations.AlterField(
            model_name='usercarteamship',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_car_teams', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='usercaseship',
            name='case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='case_users', to='modelCore.case'),
        ),
        migrations.AlterField(
            model_name='usercaseship',
            name='exclude_ids_text',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='usercaseship',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='user_cases', to=settings.AUTH_USER_MODEL),
        ),
    ]
