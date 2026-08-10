"""Payment gateway interface.

A gateway turns a TournamentPayment into a redirect to the provider, then
verifies the result when the payer returns. Two implementations exist:
BkashGateway (real) and DummyGateway (local, no credentials needed).
"""


class CreateResult:
    def __init__(self, redirect_url, gateway_payment_id, raw=None):
        self.redirect_url = redirect_url
        self.gateway_payment_id = gateway_payment_id
        self.raw = raw or {}


class ExecuteResult:
    def __init__(self, success, transaction_id="", message="", raw=None):
        self.success = success
        self.transaction_id = transaction_id
        self.message = message
        self.raw = raw or {}


class PaymentError(Exception):
    """Raised when the gateway cannot start or complete a payment."""


class BaseGateway:
    name = "base"

    def create_payment(self, payment, callback_url):
        """Start a payment; return a CreateResult with a redirect URL."""
        raise NotImplementedError

    def execute_payment(self, payment, params):
        """Finalize after the payer returns; return an ExecuteResult.

        ``params`` is the callback query dict (contains paymentID/status).
        """
        raise NotImplementedError
