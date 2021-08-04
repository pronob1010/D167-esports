# Generated by Django 3.2.5 on 2021-08-04 09:11

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0002_rename_team_teamplayers_team_name'),
        ('matches', '0022_alter_playerspointtable_teamname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playerspointtable',
            name='teamName',
        ),
        migrations.AddField(
            model_name='playerspointtable',
            name='team_Name',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, blank=True, chained_field='Match', chained_model_field='Team', null=True, on_delete=django.db.models.deletion.CASCADE, to='teams.teamplayers'),
        ),
    ]
