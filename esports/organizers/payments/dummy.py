"""A local, credential-free gateway used when bKash isn't configured.

It simulates the provider round-trip: "creating" a payment just redirects the
browser straight back to the callback URL with a success flag, and executing
marks it paid. This lets the entire pay flow be exercised in development and
tests without contacting bKash.
"""
from .base import BaseGateway, CreateResult, ExecuteResult


class DummyGateway(BaseGateway):
    name = "dummy"

    def create_payment(self, payment, callback_url):
        gateway_payment_id = f"DUMMY-{payment.pk}"
        sep = "&" if "?" in callback_url else "?"
        # Send the payer straight back as if bKash approved the payment.
        redirect_url = (
            f"{callback_url}{sep}paymentID={gateway_payment_id}&status=success"
        )
        return CreateResult(redirect_url, gateway_payment_id)

    def execute_payment(self, payment, params):
        if params.get("status") != "success":
            return ExecuteResult(False, message="Payment was not completed.")
        return ExecuteResult(
            True,
            transaction_id=f"DUMMYTRX{payment.pk}",
            message="Paid (dummy gateway).",
        )
