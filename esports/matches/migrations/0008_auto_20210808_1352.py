# Generated by Django 3.2.5 on 2021-08-08 07:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0007_auto_20210808_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchgroup',
            name='Tournament',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='matches.tournament'),
        ),
        migrations.AddField(
            model_name='matchround',
            name='Tournament',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='matches.tournament'),
        ),
    ]