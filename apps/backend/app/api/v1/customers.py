import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_company_access, CurrentUser
from app.models.customer import Customer
from app.models.device import Device
from app.models.service_order import ServiceOrder
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter()


@router.get("", response_model=list[CustomerResponse])
def list_customers(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = None,
):
    query = db.query(Customer).filter(
        Customer.company_id == user.company_id,
        Customer.deleted_at.is_(None),
    )
    if q:
        query = query.filter(
            Customer.name.ilike(f"%{q}%")
            | Customer.phone.ilike(f"%{q}%")
            | Customer.document.ilike(f"%{q}%")
        )
    return query.order_by(Customer.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(
    payload: CustomerCreate,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    customer = Customer(
        company_id=user.company_id,
        name=payload.name,
        document=payload.document,
        phone=payload.phone,
        whatsapp=payload.whatsapp,
        email=payload.email,
        notes=payload.notes,
        is_active=True,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.company_id == user.company_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: uuid.UUID,
    payload: CustomerUpdate,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.company_id == user.company_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.company_id == user.company_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    customer.deleted_at = datetime.now(timezone.utc)
    customer.is_active = False
    db.commit()
    return {"message": "Cliente removido"}


@router.get("/{customer_id}/devices")
def list_customer_devices(
    customer_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.company_id == user.company_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    devices = (
        db.query(Device)
        .filter(
            Device.customer_id == customer_id,
            Device.company_id == user.company_id,
            Device.deleted_at.is_(None),
        )
        .order_by(Device.created_at.desc())
        .all()
    )
    return [
        {
            "id": str(d.id),
            "category": d.category,
            "brand": d.brand,
            "model": d.model,
            "color": d.color,
            "imei": d.imei,
            "serial_number": d.serial_number,
            "created_at": d.created_at.isoformat(),
        }
        for d in devices
    ]


@router.get("/{customer_id}/service-orders")
def list_customer_service_orders(
    customer_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.company_id == user.company_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    orders = (
        db.query(ServiceOrder)
        .filter(
            ServiceOrder.customer_id == customer_id,
            ServiceOrder.company_id == user.company_id,
            ServiceOrder.deleted_at.is_(None),
        )
        .order_by(ServiceOrder.created_at.desc())
        .all()
    )
    return [
        {
            "id": str(o.id),
            "os_number": o.os_number,
            "status": o.status,
            "problem_reported": o.problem_reported,
            "entry_at": o.entry_at.isoformat() if o.entry_at else None,
            "created_at": o.created_at.isoformat(),
        }
        for o in orders
    ]
