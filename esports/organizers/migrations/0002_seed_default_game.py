from django.db import migrations
from django.utils.text import slugify


def seed_games(apps, schema_editor):
    Game = apps.get_model("organizers", "Game")
    defaults = [
        ("Turf Football", 7, "Small-sided turf football tournaments."),
    ]
    for name, team_size, description in defaults:
        Game.objects.get_or_create(
            name=name,
            defaults={
                "slug": slugify(name),
                "default_team_size": team_size,
                "description": description,
                "is_active": True,
            },
        )


def unseed_games(apps, schema_editor):
    Game = apps.get_model("organizers", "Game")
    Game.objects.filter(name="Turf Football").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_games, unseed_games),
    ]
