from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


class Game(models.Model):
    """A game type the platform supports (e.g. Turf Football, Cricket).

    Adding a new game is a data row, not a code change - this is what makes the
    platform multi-game ("day by day we add more games").
    """
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    description = models.TextField(max_length=300, blank=True)
    # Sensible default squad size for this game (11 for football, etc.).
    default_team_size = models.PositiveIntegerField(default=11)
    icon = models.ImageField(upload_to="games", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Organizer(models.Model):
    """A tenant on the platform: a person/organization that hosts tournaments.

    Every organizer only ever sees and manages their own data. This is the
    core of the multi-tenant design.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organizer",
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    logo = models.ImageField(upload_to="organizers", null=True, blank=True)
    about = models.TextField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "organizer"
            slug = base
            counter = 2
            # Ensure a unique slug even if two organizers pick the same name.
            while Organizer.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TournamentPayment(models.Model):
    """Records the per-tournament fee an organizer owes to run a tournament.

    The chosen business model is "fee per tournament". This model captures the
    charge; the actual payment gateway (bKash/Nagad/Stripe) is intentionally
    NOT wired up yet - see PLATFORM_ROADMAP.md (Stage D).
    """
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_WAIVED = "waived"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_WAIVED, "Waived"),
    ]

    organizer = models.ForeignKey(
        Organizer,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    tournament = models.OneToOneField(
        "matches.Tournament",
        on_delete=models.CASCADE,
        related_name="payment",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tournament} - {self.amount} ({self.status})"
