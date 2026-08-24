import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.subscription import Subscription, Payment
from app.models.plan import Plan
from app.models.company import Company
from app.integrations.mercadopago.client import mp_client


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db

    def get_active(self, company_id: uuid.UUID) -> Subscription | None:
        return (
            self.db.query(Subscription)
            .filter(
                Subscription.company_id == company_id,
                Subscription.status.in_(["ACTIVE", "TRIAL", "PAST_DUE"]),
            )
            .order_by(Subscription.created_at.desc())
            .first()
        )

    def get_or_create_trial(self, company_id: uuid.UUID, plan_id: uuid.UUID) -> Subscription:
        sub = self.get_active(company_id)
        if sub:
            return sub
        sub = Subscription(
            company_id=company_id,
            plan_id=plan_id,
            status="TRIAL",
            trial_ends_at=datetime.now(timezone.utc) + timedelta(days=7),
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)
        return sub

    def checkout(self, company_id: uuid.UUID, plan_id: uuid.UUID) -> dict | None:
        plan = self.db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            return None

        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return None

        sub = self.get_active(company_id)
        if sub and sub.status in ["ACTIVE", "TRIAL"]:
            return {"subscription_id": str(sub.id), "status": sub.status}

        if plan.mercadopago_plan_id and mp_client.access_token:
            result = mp_client.create_pre_approval(
                plan.mercadopago_plan_id,
                company.email or "",
                f"Assinatura Lotec - {plan.name}",
            )
            if result:
                sub = Subscription(
                    company_id=company_id,
                    plan_id=plan_id,
                    provider="mercadopago",
                    provider_subscription_id=result.get("id"),
                    status="PENDING",
                    started_at=datetime.now(timezone.utc),
                )
                self.db.add(sub)
                self.db.commit()
                return {"checkout_url": result.get("init_point"), "subscription_id": str(sub.id)}

        sub = Subscription(
            company_id=company_id,
            plan_id=plan_id,
            status="ACTIVE",
            started_at=datetime.now(timezone.utc),
            next_billing_date=datetime.now(timezone.utc) + timedelta(days=30),
        )
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)
        return {"subscription_id": str(sub.id), "status": "ACTIVE"}

    def change_plan(self, company_id: uuid.UUID, plan_id: uuid.UUID) -> Subscription | None:
        sub = self.get_active(company_id)
        if not sub:
            return None
        sub.plan_id = plan_id
        self.db.commit()
        self.db.refresh(sub)
        return sub

    def cancel(self, company_id: uuid.UUID) -> Subscription | None:
        sub = self.get_active(company_id)
        if not sub:
            return None
        if sub.provider_subscription_id and mp_client.access_token:
            mp_client.cancel_pre_approval(sub.provider_subscription_id)
        sub.status = "CANCELED"
        sub.canceled_at = datetime.now(timezone.utc)
        sub.ended_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(sub)
        return sub

    def process_webhook(self, event_type: str, resource_id: str, payload: dict) -> None:
        if event_type == "payment":
            self._process_payment_webhook(resource_id, payload)
        elif event_type == "preapproval":
            self._process_subscription_webhook(resource_id, payload)

    def _process_payment_webhook(self, payment_id: str, payload: dict) -> None:
        mp_data = mp_client.get_payment(payment_id) if mp_client.access_token else payload
        if not mp_data:
            return

        provider_status = mp_data.get("status", "")
        normalized = mp_client.normalize_payment_status(provider_status)

        existing = (
            self.db.query(Payment)
            .filter(Payment.provider == "mercadopago", Payment.provider_payment_id == payment_id)
            .first()
        )
        if existing:
            existing.status = normalized
            existing.provider_status = provider_status
            existing.payload = mp_data
            self.db.commit()
            return

        subscription_id = mp_data.get("preapproval_id")
        sub = None
        if subscription_id:
            sub = (
                self.db.query(Subscription)
                .filter(Subscription.provider_subscription_id == subscription_id)
                .first()
            )

        payment = Payment(
            company_id=sub.company_id if sub else None,
            subscription_id=sub.id if sub else None,
            provider="mercadopago",
            provider_payment_id=payment_id,
            status=normalized,
            provider_status=provider_status,
            amount=mp_data.get("transaction_amount"),
            currency=mp_data.get("currency_id", "BRL"),
            paid_at=datetime.fromtimestamp(mp_data.get("date_approved", 0), tz=timezone.utc)
            if mp_data.get("date_approved")
            else None,
            payload=mp_data,
        )
        self.db.add(payment)
        self.db.commit()

    def _process_subscription_webhook(self, preapproval_id: str, payload: dict) -> None:
        mp_data = mp_client.get_pre_approval(preapproval_id) if mp_client.access_token else payload
        if not mp_data:
            return

        sub = (
            self.db.query(Subscription)
            .filter(Subscription.provider_subscription_id == preapproval_id)
            .first()
        )
        if not sub:
            return

        provider_status = mp_data.get("status", "")
        normalized = mp_client.normalize_subscription_status(provider_status)

        sub.provider_status = provider_status
        if normalized in ["ACTIVE", "SUSPENDED", "CANCELED", "EXPIRED"]:
            sub.status = normalized
        if normalized == "CANCELED":
            sub.canceled_at = datetime.now(timezone.utc)
        self.db.commit()
