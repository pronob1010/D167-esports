"""Registration notifications.

Email only for now (console backend in dev). SMS for local captains can be
added behind these same two functions later without touching the views.
All sends are best-effort: a mail failure must never break the web request.
"""
import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _send(subject, body, recipient):
    if not recipient:
        return
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=True,
        )
    except Exception:  # pragma: no cover - defensive; never break the request
        logger.exception("Failed to send notification email to %s", recipient)


def notify_new_registration(registration):
    """Tell the organizer a team has registered."""
    organizer = registration.tournament.organizer
    recipient = ""
    if organizer:
        recipient = organizer.contact_email or (
            organizer.user.email if organizer.user else ""
        )
    subject = f"New team registration: {registration.team_name}"
    body = (
        f"{registration.team_name} has registered for "
        f"{registration.tournament.Tournament_title}.\n\n"
        f"Captain: {registration.captain_name} ({registration.captain_phone})\n"
        f"Review pending registrations in your dashboard."
    )
    _send(subject, body, recipient)


def notify_registration_decided(registration):
    """Tell the captain their registration was approved or rejected."""
    subject = (
        f"Your registration for {registration.tournament.Tournament_title} "
        f"was {registration.get_status_display().lower()}"
    )
    body = (
        f"Hi {registration.captain_name},\n\n"
        f"Your team '{registration.team_name}' has been "
        f"{registration.get_status_display().lower()} for "
        f"{registration.tournament.Tournament_title}."
    )
    if registration.note:
        body += f"\n\nNote from the organizer: {registration.note}"
    _send(subject, body, registration.captain_email)
