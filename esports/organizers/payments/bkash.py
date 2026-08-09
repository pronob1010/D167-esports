"""bKash Tokenized Checkout (PGW) gateway.

Flow: grant token -> create payment (get bKash URL) -> redirect payer ->
bKash returns to our callback with paymentID + status -> execute payment.

Docs: https://developer.bka.sh/ (Tokenized Checkout / Checkout URL).
Credentials come from settings (env). This talks to the live/sandbox API, so
it is exercised via the DummyGateway in tests rather than over the network.
"""
import time

from django.conf import settings

from .base import BaseGateway, CreateResult, ExecuteResult, PaymentError


class BkashGateway(BaseGateway):
    name = "bkash"

    def __init__(self):
        self.base_url = settings.BKASH_BASE_URL.rstrip("/")
        self.app_key = settings.BKASH_APP_KEY
        self.app_secret = settings.BKASH_APP_SECRET
        self.username = settings.BKASH_USERNAME
        self.password = settings.BKASH_PASSWORD
        self._token = None
        self._token_expiry = 0

    # --- low-level helpers -------------------------------------------------
    def _request(self, method, path, headers=None, json=None):
        import requests  # lazy so dummy-only installs don't need it

        url = f"{self.base_url}{path}"
        try:
            resp = requests.request(
                method, url, headers=headers, json=json, timeout=30
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:  # network / HTTP error
            raise PaymentError(f"bKash request failed: {exc}") from exc
        except ValueError as exc:  # non-JSON body
            raise PaymentError("bKash returned an invalid response.") from exc

    def _grant_token(self):
        now = time.time()
        if self._token and now < self._token_expiry:
            return self._token
        data = self._request(
            "POST",
            "/tokenized/checkout/token/grant",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "username": self.username,
                "password": self.password,
            },
            json={"app_key": self.app_key, "app_secret": self.app_secret},
        )
        token = data.get("id_token")
        if not token:
            raise PaymentError(f"bKash token grant failed: {data}")
        # Refresh a minute before the stated expiry.
        self._token = token
        self._token_expiry = now + int(data.get("expires_in", 3600)) - 60
        return token

    def _auth_headers(self):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": self._grant_token(),
            "X-APP-Key": self.app_key,
        }

    # --- gateway interface -------------------------------------------------
    def create_payment(self, payment, callback_url):
        data = self._request(
            "POST",
            "/tokenized/checkout/create",
            headers=self._auth_headers(),
            json={
                "mode": "0011",  # URL-based tokenized checkout
                "payerReference": str(payment.organizer_id or ""),
                "callbackURL": callback_url,
                "amount": f"{payment.amount:.2f}",
                "currency": "BDT",
                "intent": "sale",
                "merchantInvoiceNumber": f"D167-{payment.pk}",
            },
        )
        payment_id = data.get("paymentID")
        redirect_url = data.get("bkashURL")
        if not payment_id or not redirect_url:
            raise PaymentError(f"bKash create failed: {data}")
        return CreateResult(redirect_url, payment_id, raw=data)

    def execute_payment(self, payment, params):
        # bKash sends status=success|failure|cancel back to the callback.
        if params.get("status") != "success":
            return ExecuteResult(
                False, message=f"Payment {params.get('status', 'not completed')}."
            )
        payment_id = params.get("paymentID") or payment.gateway_payment_id
        data = self._request(
            "POST",
            "/tokenized/checkout/execute",
            headers=self._auth_headers(),
            json={"paymentID": payment_id},
        )
        if data.get("statusCode") == "0000" and data.get("transactionStatus") == "Completed":
            return ExecuteResult(
                True,
                transaction_id=data.get("trxID", ""),
                message="Payment completed.",
                raw=data,
            )
        return ExecuteResult(
            False,
            message=data.get("statusMessage", "Payment could not be verified."),
            raw=data,
        )
