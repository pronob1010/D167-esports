# Generated by Django 3.2.5 on 2021-08-08 08:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0009_alter_matchround_tournament'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='Tournament',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='matches.tournament'),
        ),
        migrations.AlterField(
            model_name='matchgroup',
            name='Tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matches.tournament'),
        ),
    ]
