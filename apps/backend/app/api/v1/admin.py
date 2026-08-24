import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import require_super_admin, CurrentUser
from app.models.company import Company
from app.models.subscription import Subscription, Payment, WebhookEvent
from app.models.plan import Plan
from app.models.user import User
from app.models.company_user import CompanyUser
from app.models.service_order import ServiceOrder
from app.models.customer import Customer

from app.models.system_setting import SystemSetting

router = APIRouter()


@router.get("/dashboard")
def admin_dashboard(
    user: CurrentUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    total_companies = db.query(func.count(Company.id)).filter(Company.deleted_at.is_(None)).scalar() or 0
    active_companies = db.query(func.count(Company.id)).filter(Company.deleted_at.is_(None), Company.status == "ACTIVE").scalar() or 0
    suspended_companies = db.query(func.count(Company.id)).filter(Company.deleted_at.is_(None), Company.status == "SUSPENDED").scalar() or 0

    total_users = db.query(func.count(User.id)).filter(User.deleted_at.is_(None)).scalar() or 0
    total_os = db.query(func.count(ServiceOrder.id)).filter(ServiceOrder.deleted_at.is_(None)).scalar() or 0

    subs_by_plan = dict(
        db.query(Plan.name, func.count(Subscription.id))
        .join(Subscription, Subscription.plan_id == Plan.id)
        .filter(Subscription.status.in_(["ACTIVE", "TRIAL"]))
        .group_by(Plan.name)
        .all()
    )

    mrr = db.query(func.sum(Plan.price_monthly)).join(
        Subscription, Subscription.plan_id == Plan.id
    ).filter(Subscription.status == "ACTIVE").scalar() or 0

    failed_webhooks = db.query(func.count(WebhookEvent.id)).filter(
        WebhookEvent.processing_status == "FAILED"
    ).scalar() or 0

    return {
        "total_companies": total_companies,
        "active_companies": active_companies,
        "suspended_companies": suspended_companies,
        "total_users": total_users,
        "total_os": total_os,
        "subscriptions_by_plan": subs_by_plan,
        "mrr": float(mrr),
        "failed_webhooks": failed_webhooks,
    }


@router.get("/companies")
def list_companies(
    user: CurrentUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = db.query(Company).filter(Company.deleted_at.is_(None))
    total = query.count()
    companies = query.order_by(Company.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    result = []
    for c in companies:
        sub = db.query(Subscription).filter(
            Subscription.company_id == c.id,
            Subscription.status.in_(["ACTIVE", "TRIAL"]),
        ).first()
        user_count = db.query(func.count(CompanyUser.id)).filter(
            CompanyUser.company_id == c.id, CompanyUser.status == "ACTIVE"
        ).scalar() or 0
        os_count = db.query(func.count(ServiceOrder.id)).filter(
            ServiceOrder.company_id == c.id, ServiceOrder.deleted_at.is_(None)
        ).scalar() or 0
        plan = db.query(Plan).filter(Plan.id == sub.plan_id).first() if sub else None

        result.append({
            "id": str(c.id),
            "name": c.name,
            "status": c.status,
            "plan": plan.name if plan else "Nenhum",
            "user_count": user_count,
            "os_count": os_count,
            "created_at": c.created_at.isoformat(),
        })

    import math
    return {
        "items": result,
        "total": total,
        "pages": math.ceil(total / page_size) if total > 0 else 0,
    }


@router.get("/companies/{company_id}")
def get_company(
    company_id: uuid.UUID,
    user: CurrentUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    sub = db.query(Subscription).filter(Subscription.company_id == company_id).first()
    users = db.query(CompanyUser).filter(CompanyUser.company_id == company_id, CompanyUser.status == "ACTIVE").all()
    return {
        "company": company,
        "subscription": sub,
        "user_count": len(users),
    }


@router.patch("/companies/{company_id}/status")
def update_company_status(
    company_id: uuid.UUID,
    body: dict,
    user: CurrentUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    new_status = body.get("status")
    if new_status not in ["ACTIVE", "SUSPENDED", "BLOCKED", "INACTIVE"]:
        raise HTTPException(status_code=400, detail="Status inválido")
    company.status = new_status
    db.commit()
    return {"message": f"Empresa {new_status.lower()}"}


@router.get("/subscriptions")
def list_subscriptions(
    user: CurrentUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = db.query(Subscription)
    total = query.count()
    subs = query.order_by(Subscription.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    import math
    return {
        "items": [
            {
                "id": str(s.id),
                "company_id": str(s.company_id),
                "plan_id": str(s.plan_id),
                "status": s.status,
                "provider_status": s.provider_status,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "next_billing_date": s.next_billing_date.isoformat() if s.next_billing_date else None,
                "created_at": s.created_at.isoformat(),
            }
            for s in subs
        ],
        "total": total,
        "pages": math.ceil(total / page_size) if total > 0 else 0,
    }


@router.get("/payments")
def list_payments(
    user: CurrentUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = db.query(Payment)
    total = query.count()
    payments = query.order_by(Payment.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    import math
    return {
        "items": [
            {
                "id": str(p.id),
                "company_id": str(p.company_id) if p.company_id else None,
                "status": p.status,
                "amount": float(p.amount) if p.amount else None,
                "paid_at": p.paid_at.isoformat() if p.paid_at else None,
                "created_at": p.created_at.isoformat(),
            }
            for p in payments
        ],
        "total": total,
        "pages": math.ceil(total / page_size) if total > 0 else 0,
    }


@router.get("/webhook-events")
def list_webhook_events(
    user: CurrentUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = db.query(WebhookEvent)
    total = query.count()
    events = query.order_by(WebhookEvent.received_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    import math
    return {
        "items": [
            {
                "id": str(e.id),
                "provider": e.provider,
                "event_type": e.event_type,
                "action": e.action,
                "signature_valid": e.signature_valid,
                "processing_status": e.processing_status,
                "processing_error": e.processing_error,
                "received_at": e.received_at.isoformat(),
                "processed_at": e.processed_at.isoformat() if e.processed_at else None,
            }
            for e in events
        ],
        "total": total,
        "pages": math.ceil(total / page_size) if total > 0 else 0,
    }


@router.get("/plans")
def list_plans_admin(
    user: CurrentUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    plans = db.query(Plan).order_by(Plan.display_order).all()
    return [
        {
            "id": str(p.id),
            "code": p.code,
            "name": p.name,
            "price_monthly": float(p.price_monthly),
            "active": p.active,
            "mercadopago_plan_id": p.mercadopago_plan_id,
        }
        for p in plans
    ]


@router.put("/plans/{plan_id}")
def update_plan(
    plan_id: uuid.UUID,
    body: dict,
    user: CurrentUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    for field in ["name", "description", "price_monthly", "active", "mercadopago_plan_id"]:
        if field in body:
            setattr(plan, field, body[field])
    db.commit()
    return {"message": "Plano atualizado"}


@router.get("/settings")
def list_settings(
    user: CurrentUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    settings = db.query(SystemSetting).all()
    return {s.key: {"value": s.value, "description": s.description} for s in settings}


@router.put("/settings")
def update_settings(
    body: dict,
    user: CurrentUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    for key, value in body.items():
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if setting:
            setting.value = str(value) if value is not None else None
        else:
            db.add(SystemSetting(key=key, value=str(value) if value is not None else None))
    db.commit()
    return {"message": "Configurações atualizadas"}
