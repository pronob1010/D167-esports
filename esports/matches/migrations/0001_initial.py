# Generated by Django 3.2.5 on 2021-08-05 11:09

from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Match_Title', models.CharField(max_length=100)),
                ('Featured', models.BooleanField(default=False)),
                ('Countdown_Expected', models.BooleanField(default=False)),
                ('TimeDate', models.DateTimeField(blank=True, null=True)),
                ('MatchAbout', models.TextField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SEASON',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SEASON_title', models.CharField(max_length=25)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='RegisteredTeams',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Win', models.BooleanField(blank=True, default=False, null=True)),
                ('Placement_Point', models.IntegerField(default=0)),
                ('total_Point', models.PositiveIntegerField(default=0)),
                ('Match', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='matches.match')),
                ('Team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='teams.team')),
            ],
        ),
        migrations.CreateModel(
            name='PlayersPointTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kill_Point', models.PositiveBigIntegerField(default=0)),
                ('Match', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='matches.match')),
                ('player', smart_selects.db_fields.GroupedForeignKey(blank=True, group_field='player', null=True, on_delete=django.db.models.deletion.CASCADE, to='teams.teamplayers')),
                ('teamName', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='matches.registeredteams')),
            ],
        ),
        migrations.CreateModel(
            name='MatchRound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Round_title', models.CharField(max_length=25)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('Season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matches.season')),
            ],
        ),
        migrations.CreateModel(
            name='MatchGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Group_title', models.CharField(max_length=25)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('Round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matches.matchround')),
                ('Season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matches.season')),
            ],
        ),
        migrations.AddField(
            model_name='match',
            name='Match_Group',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='matches.matchgroup'),
        ),
        migrations.AddField(
            model_name='match',
            name='Match_Round',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='matches.matchround'),
        ),
        migrations.AddField(
            model_name='match',
            name='Match_SEASON',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='matches.season'),
        ),
    ]
