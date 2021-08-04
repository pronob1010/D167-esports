# Generated by Django 3.2.5 on 2021-08-03 21:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0002_alter_player_speciality'),
        ('matches', '0004_alter_match_match_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerspointtable',
            name='player',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='players.player'),
        ),
    ]
