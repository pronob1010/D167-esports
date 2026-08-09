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

    # --- Per-game scoring rules -------------------------------------------
    # These make standings game-aware: football uses 3/1/0 and "goals",
    # cricket uses 2/1/0 and "runs". A new game is still just a data row.
    points_win = models.PositiveIntegerField(default=3)
    points_draw = models.PositiveIntegerField(default=1)
    points_loss = models.PositiveIntegerField(default=0)
    score_noun = models.CharField(max_length=20, default="goals")  # e.g. "runs"
    draw_label = models.CharField(max_length=20, default="Draw")   # e.g. "Tie"

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
    """The per-tournament fee an organizer owes to run a tournament.

    Business model: "fee per tournament". Paid via bKash Tokenized Checkout
    (see organizers/payments/). A zero fee is auto-waived.
    """
    STATUS_PENDING = "pending"       # owed, not started
    STATUS_INITIATED = "initiated"   # redirected to the gateway
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_WAIVED = "waived"         # nothing to pay / comped
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_INITIATED, "Initiated"),
        (STATUS_PAID, "Paid"),
        (STATUS_FAILED, "Failed"),
        (STATUS_WAIVED, "Waived"),
    ]

    # Statuses that mean "the organizer may go live".
    SETTLED_STATUSES = (STATUS_PAID, STATUS_WAIVED)

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
    # Gateway tracking.
    gateway = models.CharField(max_length=20, blank=True)          # e.g. "bkash"
    gateway_payment_id = models.CharField(max_length=100, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)  # bKash trxID
    created_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_settled(self):
        return self.status in self.SETTLED_STATUSES

    def __str__(self):
        return f"{self.tournament} - {self.amount} ({self.status})"
