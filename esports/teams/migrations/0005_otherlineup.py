# Generated by Django 3.2.5 on 2021-08-12 21:29

from django.db import migrations, models
import django.db.models.deletion
import teams.models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0004_centralteam_centralteamachievement'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtherLineUp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('baseteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.centralteam')),
                ('team', models.ForeignKey(blank=True, null=teams.models.Team, on_delete=django.db.models.deletion.CASCADE, to='teams.team')),
            ],
        ),
    ]
