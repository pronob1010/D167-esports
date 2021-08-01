# Generated by Django 3.2.5 on 2021-08-01 21:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matche',
            name='Match_Category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category', to='matches.matche_categories'),
        ),
        migrations.AlterField(
            model_name='matche',
            name='Match_Level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category', to='matches.matche_level'),
        ),
    ]
