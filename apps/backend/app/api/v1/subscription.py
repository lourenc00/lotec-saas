import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_company_access, require_admin, CurrentUser
from app.models.subscription import Subscription
from app.models.plan import Plan
from app.schemas.subscription import (
    SubscriptionResponse,
    CheckoutRequest,
    ChangePlanRequest,
)

router = APIRouter()


@router.get("", response_model=SubscriptionResponse)
def get_subscription(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    sub = (
        db.query(Subscription)
        .filter(Subscription.company_id == user.company_id)
        .order_by(Subscription.created_at.desc())
        .first()
    )
    if not sub:
        plan = db.query(Plan).filter(Plan.code == "basic").first()
        if plan:
            sub = Subscription(
                company_id=user.company_id,
                plan_id=plan.id,
                status="TRIAL",
                trial_ends_at=datetime.now(timezone.utc),
            )
            db.add(sub)
            db.commit()
            db.refresh(sub)
        else:
            raise HTTPException(status_code=404, detail="Nenhuma assinatura encontrada")
    return sub


@router.post("/checkout")
def checkout(
    payload: CheckoutRequest,
    user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from app.services.subscription import SubscriptionService
    svc = SubscriptionService(db)
    result = svc.checkout(user.company_id, payload.plan_id)
    if not result:
        raise HTTPException(status_code=400, detail="Erro ao processar checkout")
    return result


@router.post("/change-plan")
def change_plan(
    payload: ChangePlanRequest,
    user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from app.services.subscription import SubscriptionService
    svc = SubscriptionService(db)
    sub = svc.change_plan(user.company_id, payload.plan_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    return {"message": "Plano alterado com sucesso", "subscription_id": str(sub.id)}


@router.post("/cancel")
def cancel_subscription(
    user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from app.services.subscription import SubscriptionService
    svc = SubscriptionService(db)
    sub = svc.cancel(user.company_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    return {"message": "Assinatura cancelada"}


@router.post("/regularize")
def regularize(
    user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    sub = (
        db.query(Subscription)
        .filter(
            Subscription.company_id == user.company_id,
            Subscription.status.in_(["PAST_DUE", "SUSPENDED"]),
        )
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Nenhuma assinatura para regularizar")
    return {"message": "Regularização iniciada", "subscription_id": str(sub.id)}
