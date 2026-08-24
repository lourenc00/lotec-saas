import hashlib
import hmac
import json
from datetime import datetime, timezone

import httpx

from app.core.config import settings


class MercadoPagoClient:
    BASE_URL = "https://api.mercadopago.com"

    def __init__(self):
        self.access_token = settings.MERCADOPAGO_ACCESS_TOKEN
        self.webhook_secret = settings.MERCADOPAGO_WEBHOOK_SECRET

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs) -> dict | None:
        if not self.access_token:
            return None
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.request(
                    method,
                    f"{self.BASE_URL}{path}",
                    headers=self._headers(),
                    **kwargs,
                )
                if resp.status_code >= 400:
                    return None
                return resp.json()
        except Exception:
            return None

    def create_pre_approval(self, plan_mp_id: str, payer_email: str, reason: str) -> dict | None:
        data = {
            "preapproval_plan_id": plan_mp_id,
            "payer_email": payer_email,
            "reason": reason,
            "auto_recurring": {
                "frequency": 1,
                "frequency_type": "months",
                "transaction_amount": 0,
                "currency_id": "BRL",
            },
        }
        return self._request("POST", "/v1/payment_intentions", json=data)

    def get_pre_approval(self, preapproval_id: str) -> dict | None:
        return self._request("GET", f"/v1/payment_intentions/{preapproval_id}")

    def cancel_pre_approval(self, preapproval_id: str) -> dict | None:
        return self._request("PUT", f"/v1/payment_intentions/{preapproval_id}", json={"status": "cancelled"})

    def get_payment(self, payment_id: str) -> dict | None:
        return self._request("GET", f"/v1/payments/{payment_id}")

    def create_preference(self, items: list, payer_email: str | None = None) -> dict | None:
        data = {
            "items": items,
            "payment_methods": {"installments": 1},
        }
        if payer_email:
            data["payer"] = {"email": payer_email}
        return self._request("POST", "/checkout/preferences", json=data)

    def validate_webhook_signature(self, body: bytes, headers: dict) -> bool:
        if not self.webhook_secret:
            return True
        x_signature = headers.get("x-signature", "")
        x_request_id = headers.get("x-request-id", "")
        try:
            parts = {}
            for part in x_signature.split(","):
                k, v = part.split("=", 1)
                parts[k.strip()] = v.strip()
            ts = parts.get("ts", "")
            v1 = parts.get("v1", "")
            signed_payload = f"{ts}.{body.decode()}.{x_request_id}"
            expected = hmac.new(
                self.webhook_secret.encode(), signed_payload.encode(), hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(v1, expected)
        except Exception:
            return False

    @staticmethod
    def normalize_subscription_status(mp_status: str) -> str:
        mapping = {
            "authorized": "ACTIVE",
            "paused": "SUSPENDED",
            "cancelled": "CANCELED",
            "pending": "PENDING",
            "expired": "EXPIRED",
        }
        return mapping.get(mp_status, mp_status.upper())

    @staticmethod
    def normalize_payment_status(mp_status: str) -> str:
        mapping = {
            "approved": "APPROVED",
            "pending": "PENDING",
            "authorized": "APPROVED",
            "in_process": "PENDING",
            "in_mediation": "PENDING",
            "rejected": "REJECTED",
            "cancelled": "CANCELED",
            "refunded": "REFUNDED",
            "charged_back": "CHARGED_BACK",
        }
        return mapping.get(mp_status, "UNKNOWN")


mp_client = MercadoPagoClient()
