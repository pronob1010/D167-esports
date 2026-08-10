from django.db import migrations
from django.utils.text import slugify


def seed_cricket(apps, schema_editor):
    Game = apps.get_model("organizers", "Game")
    Game.objects.get_or_create(
        name="Cricket",
        defaults={
            "slug": slugify("Cricket"),
            "default_team_size": 11,
            "description": "Cricket tournaments (runs-based scoring).",
            "is_active": True,
            "points_win": 2,
            "points_draw": 1,
            "points_loss": 0,
            "score_noun": "runs",
            "draw_label": "Tie",
        },
    )


def unseed_cricket(apps, schema_editor):
    Game = apps.get_model("organizers", "Game")
    Game.objects.filter(name="Cricket").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0004_auto_20260810_0042'),
    ]

    operations = [
        migrations.RunPython(seed_cricket, unseed_cricket),
    ]
