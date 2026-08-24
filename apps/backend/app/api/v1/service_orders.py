import uuid
import math
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import sqlalchemy

from app.core.database import get_db
from app.core.deps import require_company_access, CurrentUser
from app.models.service_order import ServiceOrder
from app.models.service_order_status_history import ServiceOrderStatusHistory
from app.models.service_order_service import ServiceOrderService
from app.models.service_order_part import ServiceOrderPart
from app.models.device import Device
from app.models.customer import Customer
from app.schemas.service_order import (
    ServiceOrderCreate,
    ServiceOrderUpdate,
    ServiceOrderStatusChange,
    ServiceOrderResponse,
    ServiceOrderListResponse,
    ServiceOrderServiceCreate,
    ServiceOrderPartCreate,
)

router = APIRouter()

VALID_TRANSITIONS = {
    "RECEIVED": ["IN_ANALYSIS", "CANCELED"],
    "IN_ANALYSIS": ["WAITING_APPROVAL", "IN_REPAIR", "CANCELED", "NO_REPAIR"],
    "WAITING_APPROVAL": ["IN_REPAIR", "CANCELED", "NO_REPAIR"],
    "WAITING_PART": ["IN_REPAIR", "CANCELED"],
    "IN_REPAIR": ["READY", "WAITING_PART", "CANCELED"],
    "READY": ["DELIVERED", "IN_REPAIR"],
    "DELIVERED": [],
    "CANCELED": [],
    "NO_REPAIR": [],
}


def _get_next_os_number(db: Session, company_id: uuid.UUID) -> int:
    result = db.execute(
        text("""
        INSERT INTO company_counters (company_id, next_os_number, updated_at)
        VALUES (:cid, 2, now())
        ON CONFLICT (company_id) DO UPDATE
        SET next_os_number = company_counters.next_os_number + 1,
            updated_at = now()
        RETURNING next_os_number - 1
        """),
        {"cid": str(company_id)},
    )
    return result.scalar()


@router.get("", response_model=ServiceOrderListResponse)
def list_service_orders(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    customer_id: uuid.UUID | None = None,
    device_id: uuid.UUID | None = None,
    q: str | None = None,
):
    query = db.query(ServiceOrder).filter(
        ServiceOrder.company_id == user.company_id,
        ServiceOrder.deleted_at.is_(None),
    )
    if status:
        query = query.filter(ServiceOrder.status == status)
    if customer_id:
        query = query.filter(ServiceOrder.customer_id == customer_id)
    if device_id:
        query = query.filter(ServiceOrder.device_id == device_id)
    if q:
        query = query.join(Customer, ServiceOrder.customer_id == Customer.id).filter(
            Customer.name.ilike(f"%{q}%")
            | Customer.phone.ilike(f"%{q}%")
            | func.cast(ServiceOrder.os_number, sqlalchemy.String).ilike(f"%{q}%")
        )

    total = query.count()
    pages = math.ceil(total / page_size) if total > 0 else 0
    items = query.order_by(ServiceOrder.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return ServiceOrderListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        pages=pages,
    )


@router.post("", response_model=ServiceOrderResponse, status_code=201)
def create_service_order(
    payload: ServiceOrderCreate,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == payload.customer_id,
            Customer.company_id == user.company_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    device = (
        db.query(Device)
        .filter(
            Device.id == payload.device_id,
            Device.company_id == user.company_id,
            Device.deleted_at.is_(None),
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Aparelho não encontrado")

    os_number = _get_next_os_number(db, user.company_id)

    so = ServiceOrder(
        company_id=user.company_id,
        os_number=os_number,
        customer_id=payload.customer_id,
        device_id=payload.device_id,
        responsible_user_id=payload.responsible_user_id,
        status="RECEIVED",
        entry_at=datetime.now(timezone.utc),
        estimated_delivery_at=payload.estimated_delivery_at,
        problem_reported=payload.problem_reported,
        service_requested=payload.service_requested,
        estimated_value=payload.estimated_value,
        created_by_user_id=user.id,
    )
    db.add(so)
    db.flush()

    history = ServiceOrderStatusHistory(
        company_id=user.company_id,
        service_order_id=so.id,
        previous_status=None,
        new_status="RECEIVED",
        changed_by_user_id=user.id,
    )
    db.add(history)

    for svc in payload.services:
        total_price = svc.quantity * svc.unit_price
        db.add(
            ServiceOrderService(
                company_id=user.company_id,
                service_order_id=so.id,
                description=svc.description,
                quantity=svc.quantity,
                unit_price=svc.unit_price,
                total_price=total_price,
            )
        )

    for part in payload.parts:
        total_price = part.quantity * part.unit_price
        db.add(
            ServiceOrderPart(
                company_id=user.company_id,
                service_order_id=so.id,
                description=part.description,
                quantity=part.quantity,
                unit_price=part.unit_price,
                total_price=total_price,
            )
        )

    db.commit()
    db.refresh(so)
    return so


@router.get("/{order_id}", response_model=ServiceOrderResponse)
def get_service_order(
    order_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    so = (
        db.query(ServiceOrder)
        .filter(
            ServiceOrder.id == order_id,
            ServiceOrder.company_id == user.company_id,
            ServiceOrder.deleted_at.is_(None),
        )
        .first()
    )
    if not so:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
    return so


@router.put("/{order_id}", response_model=ServiceOrderResponse)
def update_service_order(
    order_id: uuid.UUID,
    payload: ServiceOrderUpdate,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    so = (
        db.query(ServiceOrder)
        .filter(
            ServiceOrder.id == order_id,
            ServiceOrder.company_id == user.company_id,
            ServiceOrder.deleted_at.is_(None),
        )
        .first()
    )
    if not so:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(so, field, value)

    so.updated_by_user_id = user.id
    db.commit()
    db.refresh(so)
    return so


@router.post("/{order_id}/status", response_model=ServiceOrderResponse)
def change_status(
    order_id: uuid.UUID,
    payload: ServiceOrderStatusChange,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    so = (
        db.query(ServiceOrder)
        .filter(
            ServiceOrder.id == order_id,
            ServiceOrder.company_id == user.company_id,
            ServiceOrder.deleted_at.is_(None),
        )
        .first()
    )
    if not so:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

    allowed = VALID_TRANSITIONS.get(so.status, [])
    if payload.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Transição de {so.status} para {payload.status} não é permitida",
        )

    previous_status = so.status
    so.status = payload.status
    so.updated_by_user_id = user.id

    if payload.status == "DELIVERED" and not so.delivery_at:
        so.delivery_at = datetime.now(timezone.utc)
    if payload.status == "READY" and not so.completion_at:
        so.completion_at = datetime.now(timezone.utc)

    history = ServiceOrderStatusHistory(
        company_id=user.company_id,
        service_order_id=so.id,
        previous_status=previous_status,
        new_status=payload.status,
        changed_by_user_id=user.id,
        notes=payload.notes,
    )
    db.add(history)
    db.commit()
    db.refresh(so)
    return so


@router.get("/{order_id}/history")
def get_status_history(
    order_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    so = (
        db.query(ServiceOrder)
        .filter(
            ServiceOrder.id == order_id,
            ServiceOrder.company_id == user.company_id,
            ServiceOrder.deleted_at.is_(None),
        )
        .first()
    )
    if not so:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

    history = (
        db.query(ServiceOrderStatusHistory)
        .filter(ServiceOrderStatusHistory.service_order_id == order_id)
        .order_by(ServiceOrderStatusHistory.created_at)
        .all()
    )
    return [
        {
            "id": str(h.id),
            "previous_status": h.previous_status,
            "new_status": h.new_status,
            "changed_by_user_id": str(h.changed_by_user_id),
            "notes": h.notes,
            "created_at": h.created_at.isoformat(),
        }
        for h in history
    ]
