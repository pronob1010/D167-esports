# Generated by Django 3.2.5 on 2021-08-05 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='username',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]