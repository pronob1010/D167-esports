# Generated by Django 3.2.5 on 2021-08-01 21:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('teams', '0002_auto_20210802_0308'),
    ]

    operations = [
        migrations.CreateModel(
            name='Matche_Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Matche_Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Matche',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Featured', models.BooleanField(default=False)),
                ('Score_of_Team_1', models.PositiveBigIntegerField(default=0)),
                ('Match_Category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matches.matche_categories')),
                ('Match_Level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matches.matche_level')),
                ('Team_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1', to='teams.team')),
                ('Team_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team2', to='teams.team')),
            ],
        ),
    ]
