# Generated by Django 3.2.5 on 2021-08-03 22:01

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0002_alter_player_speciality'),
        ('matches', '0007_alter_playerspointtable_player'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerspointtable',
            name='player',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, blank=True, chained_field='Team', chained_model_field='Team', null=True, on_delete=django.db.models.deletion.CASCADE, to='players.player'),
        ),
    ]
