# Generated by Django 3.2.5 on 2021-08-12 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0007_alter_player_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='photo',
        ),
    ]