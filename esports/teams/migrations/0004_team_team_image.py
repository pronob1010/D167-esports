# Generated by Django 3.2.5 on 2021-08-04 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0003_team_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='Team_image',
            field=models.ImageField(default='../static/images/soccer/team-logo5.png', upload_to='teams'),
        ),
    ]