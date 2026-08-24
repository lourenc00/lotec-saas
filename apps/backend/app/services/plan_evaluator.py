import uuid
from dataclasses import dataclass

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.plan import Plan, PlanFeature, Feature


@dataclass
class FeatureResult:
    allowed: bool
    value: bool | int | str | None = None


class PlanEvaluator:
    def __init__(self, db: Session, company_id: uuid.UUID):
        self.db = db
        self.company_id = company_id
        self._subscription: Subscription | None = None
        self._plan: Plan | None = None
        self._features: dict[str, PlanFeature] | None = None

    @property
    def subscription(self) -> Subscription | None:
        if self._subscription is None:
            self._subscription = (
                self.db.query(Subscription)
                .filter(
                    Subscription.company_id == self.company_id,
                    Subscription.status.in_(["ACTIVE", "TRIAL"]),
                )
                .first()
            )
        return self._subscription

    @property
    def plan(self) -> Plan | None:
        if self._plan is None and self.subscription:
            self._plan = self.subscription.plan
        return self._plan

    @property
    def features(self) -> dict[str, PlanFeature]:
        if self._features is None:
            self._features = {}
            if self.plan:
                for pf in self.plan.features:
                    self._features[pf.feature.code] = pf
        return self._features

    def check(self, feature_code: str) -> FeatureResult:
        pf = self.features.get(feature_code)
        if pf is None:
            return FeatureResult(allowed=False)

        if pf.feature.value_type == "boolean":
            return FeatureResult(allowed=pf.bool_value is True, value=pf.bool_value)
        elif pf.feature.value_type == "integer":
            return FeatureResult(allowed=pf.int_value is not None and pf.int_value > 0, value=pf.int_value)
        elif pf.feature.value_type == "string":
            return FeatureResult(allowed=pf.string_value is not None, value=pf.string_value)

        return FeatureResult(allowed=False)

    def require(self, feature_code: str) -> FeatureResult:
        result = self.check(feature_code)
        if not result.allowed:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "feature_not_available",
                    "message": "Este recurso não está disponível no seu plano atual.",
                },
            )
        return result

    def get_int_limit(self, feature_code: str) -> int | None:
        result = self.check(feature_code)
        return result.value if result.allowed else None


def get_plan_evaluator(db: Session, company_id: uuid.UUID) -> PlanEvaluator:
    return PlanEvaluator(db, company_id)
