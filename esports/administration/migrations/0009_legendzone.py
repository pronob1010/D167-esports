# Generated by Django 3.2.5 on 2021-08-12 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0008_alter_siteabout_banner'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegendZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, max_length=50, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='basic')),
                ('base_story', models.TextField(blank=True, max_length=500, null=True)),
                ('person_1', models.CharField(max_length=25)),
                ('story_of_person_1', models.TextField(max_length=250)),
                ('person_2', models.CharField(max_length=25)),
                ('story_of_person_2', models.TextField(max_length=250)),
            ],
        ),
    ]
