import uuid
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import require_company_access, CurrentUser
from app.models.service_order import ServiceOrder
from app.models.customer import Customer
from app.models.device import Device
from app.models.service_order_service import ServiceOrderService
from app.models.service_order_part import ServiceOrderPart

router = APIRouter()


@router.get("/summary")
def dashboard_summary(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_os = db.query(func.count(ServiceOrder.id)).filter(
        ServiceOrder.company_id == user.company_id,
        ServiceOrder.deleted_at.is_(None),
    ).scalar() or 0

    month_os = db.query(func.count(ServiceOrder.id)).filter(
        ServiceOrder.company_id == user.company_id,
        ServiceOrder.deleted_at.is_(None),
        ServiceOrder.created_at >= month_start,
    ).scalar() or 0

    total_customers = db.query(func.count(Customer.id)).filter(
        Customer.company_id == user.company_id,
        Customer.deleted_at.is_(None),
    ).scalar() or 0

    total_devices = db.query(func.count(Device.id)).filter(
        Device.company_id == user.company_id,
        Device.deleted_at.is_(None),
    ).scalar() or 0

    open_os = db.query(func.count(ServiceOrder.id)).filter(
        ServiceOrder.company_id == user.company_id,
        ServiceOrder.deleted_at.is_(None),
        ServiceOrder.status.notin_(["DELIVERED", "CANCELED", "NO_REPAIR"]),
    ).scalar() or 0

    ready_os = db.query(func.count(ServiceOrder.id)).filter(
        ServiceOrder.company_id == user.company_id,
        ServiceOrder.deleted_at.is_(None),
        ServiceOrder.status == "READY",
    ).scalar() or 0

    return {
        "total_os": total_os,
        "month_os": month_os,
        "total_customers": total_customers,
        "total_devices": total_devices,
        "open_os": open_os,
        "ready_os": ready_os,
    }


@router.get("/service-orders")
def dashboard_service_orders(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=7, le=365),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(ServiceOrder.status, func.count(ServiceOrder.id))
        .filter(
            ServiceOrder.company_id == user.company_id,
            ServiceOrder.deleted_at.is_(None),
            ServiceOrder.created_at >= since,
        )
        .group_by(ServiceOrder.status)
        .all()
    )
    return {status: count for status, count in rows}


@router.get("/services")
def dashboard_services(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=7, le=365),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(
            ServiceOrderService.description,
            func.sum(ServiceOrderService.quantity).label("total_qty"),
            func.sum(ServiceOrderService.total_price).label("total_revenue"),
        )
        .join(ServiceOrder, ServiceOrderService.service_order_id == ServiceOrder.id)
        .filter(
            ServiceOrder.company_id == user.company_id,
            ServiceOrder.deleted_at.is_(None),
            ServiceOrder.created_at >= since,
        )
        .group_by(ServiceOrderService.description)
        .order_by(func.sum(ServiceOrderService.total_price).desc())
        .limit(10)
        .all()
    )
    return [
        {"description": r[0], "total_qty": float(r[1] or 0), "total_revenue": float(r[2] or 0)}
        for r in rows
    ]


@router.get("/technicians")
def dashboard_technicians(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=7, le=365),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(
            ServiceOrder.responsible_user_id,
            func.count(ServiceOrder.id).label("os_count"),
        )
        .filter(
            ServiceOrder.company_id == user.company_id,
            ServiceOrder.deleted_at.is_(None),
            ServiceOrder.created_at >= since,
            ServiceOrder.responsible_user_id.isnot(None),
        )
        .group_by(ServiceOrder.responsible_user_id)
        .order_by(func.count(ServiceOrder.id).desc())
        .all()
    )
    return [{"user_id": str(r[0]), "os_count": r[1]} for r in rows]


@router.get("/device-models")
def dashboard_device_models(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(
            Device.brand,
            Device.model,
            func.count(Device.id).label("count"),
        )
        .filter(
            Device.company_id == user.company_id,
            Device.deleted_at.is_(None),
        )
        .group_by(Device.brand, Device.model)
        .order_by(func.count(Device.id).desc())
        .limit(10)
        .all()
    )
    return [{"brand": r[0], "model": r[1], "count": r[2]} for r in rows]
