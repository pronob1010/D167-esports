# Generated by Django 3.2.5 on 2021-08-04 08:09

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0020_alter_playerspointtable_teamname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerspointtable',
            name='teamName',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, blank=True, chained_field='teamName', chained_model_field='Team_Name', null=True, on_delete=django.db.models.deletion.CASCADE, to='matches.registeredteams'),
        ),
    ]