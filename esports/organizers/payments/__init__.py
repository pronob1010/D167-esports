"""Payment gateway selection.

Uses bKash when it's enabled and fully configured; otherwise falls back to a
local dummy gateway so the pay flow always works in development.
"""
from django.conf import settings

from .base import BaseGateway, CreateResult, ExecuteResult, PaymentError
from .bkash import BkashGateway
from .dummy import DummyGateway


def bkash_configured():
    return all([
        settings.BKASH_APP_KEY,
        settings.BKASH_APP_SECRET,
        settings.BKASH_USERNAME,
        settings.BKASH_PASSWORD,
    ])


def get_gateway():
    if getattr(settings, "BKASH_ENABLED", False) and bkash_configured():
        return BkashGateway()
    return DummyGateway()


__all__ = [
    "BaseGateway", "CreateResult", "ExecuteResult", "PaymentError",
    "BkashGateway", "DummyGateway", "get_gateway", "bkash_configured",
]
