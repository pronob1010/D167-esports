# Generated by Django 3.2.5 on 2021-08-04 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0028_auto_20210804_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registeredteams',
            name='Win',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]