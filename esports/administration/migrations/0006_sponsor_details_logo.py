# Generated by Django 3.2.5 on 2021-08-12 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0005_alter_sponsor_details_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='sponsor_details',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='sponsor'),
        ),
    ]
