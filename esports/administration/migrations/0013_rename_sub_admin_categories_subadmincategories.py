# Generated by Django 3.2.5 on 2021-08-12 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0012_subadmin'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='sub_admin_categories',
            new_name='SubAdminCategories',
        ),
    ]