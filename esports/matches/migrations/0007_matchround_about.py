# Generated by Django 3.2.5 on 2021-08-09 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0006_tournament_number_of_mvp'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchround',
            name='about',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
