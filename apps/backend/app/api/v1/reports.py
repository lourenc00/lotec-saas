from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import require_company_access, CurrentUser
from app.models.service_order import ServiceOrder
from app.models.service_order_service import ServiceOrderService
from app.models.service_order_part import ServiceOrderPart

router = APIRouter()


@router.get("/service-orders")
def report_service_orders(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
    from_date: str | None = None,
    to_date: str | None = None,
    status: str | None = None,
):
    query = db.query(ServiceOrder).filter(
        ServiceOrder.company_id == user.company_id,
        ServiceOrder.deleted_at.is_(None),
    )
    if from_date:
        query = query.filter(ServiceOrder.created_at >= from_date)
    if to_date:
        query = query.filter(ServiceOrder.created_at <= to_date)
    if status:
        query = query.filter(ServiceOrder.status == status)

    total = query.count()
    by_status = dict(
        db.query(ServiceOrder.status, func.count(ServiceOrder.id))
        .filter(
            ServiceOrder.company_id == user.company_id,
            ServiceOrder.deleted_at.is_(None),
        )
        .group_by(ServiceOrder.status)
        .all()
    )

    revenue = db.query(func.sum(ServiceOrderService.total_price)).join(
        ServiceOrder, ServiceOrderService.service_order_id == ServiceOrder.id
    ).filter(
        ServiceOrder.company_id == user.company_id,
        ServiceOrder.deleted_at.is_(None),
    ).scalar() or 0

    parts_cost = db.query(func.sum(ServiceOrderPart.total_price)).join(
        ServiceOrder, ServiceOrderPart.service_order_id == ServiceOrder.id
    ).filter(
        ServiceOrder.company_id == user.company_id,
        ServiceOrder.deleted_at.is_(None),
    ).scalar() or 0

    return {
        "total_os": total,
        "by_status": by_status,
        "services_revenue": float(revenue),
        "parts_cost": float(parts_cost),
        "margin": float(revenue) - float(parts_cost),
    }


@router.get("/services")
def report_services(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
    from_date: str | None = None,
    to_date: str | None = None,
):
    query = (
        db.query(
            ServiceOrderService.description,
            func.sum(ServiceOrderService.quantity).label("total_qty"),
            func.sum(ServiceOrderService.total_price).label("total_revenue"),
            func.count(ServiceOrderService.id).label("occurrences"),
        )
        .join(ServiceOrder, ServiceOrderService.service_order_id == ServiceOrder.id)
        .filter(
            ServiceOrder.company_id == user.company_id,
            ServiceOrder.deleted_at.is_(None),
        )
    )
    if from_date:
        query = query.filter(ServiceOrder.created_at >= from_date)
    if to_date:
        query = query.filter(ServiceOrder.created_at <= to_date)

    rows = (
        query.group_by(ServiceOrderService.description)
        .order_by(func.sum(ServiceOrderService.total_price).desc())
        .all()
    )
    return [
        {
            "description": r[0],
            "total_qty": float(r[1] or 0),
            "total_revenue": float(r[2] or 0),
            "occurrences": r[3],
        }
        for r in rows
    ]


@router.get("/device-models")
def report_device_models(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    from app.models.device import Device

    rows = (
        db.query(
            Device.brand,
            Device.model,
            func.count(ServiceOrder.id).label("os_count"),
        )
        .join(ServiceOrder, ServiceOrder.device_id == Device.id)
        .filter(
            Device.company_id == user.company_id,
            ServiceOrder.deleted_at.is_(None),
        )
        .group_by(Device.brand, Device.model)
        .order_by(func.count(ServiceOrder.id).desc())
        .limit(20)
        .all()
    )
    return [{"brand": r[0], "model": r[1], "os_count": r[2]} for r in rows]
