# Generated by Django 3.2.5 on 2021-08-06 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0003_match_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='image',
            field=models.ImageField(blank=True, default='../static/images/715035.png', null=True, upload_to='matches'),
        ),
    ]
