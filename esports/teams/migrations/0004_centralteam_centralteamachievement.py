# Generated by Django 3.2.5 on 2021-08-12 21:22

from django.db import migrations, models
import django.db.models.deletion
import teams.models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0003_remove_team_game'),
    ]

    operations = [
        migrations.CreateModel(
            name='CentralTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.CharField(max_length=40)),
                ('Team_Banner', models.ImageField(blank=True, default='../static/images/147198.jpg', null=True, upload_to='teams')),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('BS_team', models.ForeignKey(blank=True, null=teams.models.Team, on_delete=django.db.models.deletion.CASCADE, to='teams.team')),
            ],
        ),
        migrations.CreateModel(
            name='CentralTeamAchievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('story', models.TextField(blank=True, max_length=150, null=True)),
                ('Banner', models.ImageField(blank=True, default='../static/images/147198.jpg', null=True, upload_to='teams')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.centralteam')),
            ],
        ),
    ]