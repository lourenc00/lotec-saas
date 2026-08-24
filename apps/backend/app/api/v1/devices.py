import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_company_access, CurrentUser
from app.models.device import Device
from app.models.customer import Customer
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse

router = APIRouter()


@router.get("", response_model=list[DeviceResponse])
def list_devices(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = None,
):
    query = db.query(Device).filter(
        Device.company_id == user.company_id,
        Device.deleted_at.is_(None),
    )
    if q:
        query = query.filter(
            Device.model.ilike(f"%{q}%")
            | Device.brand.ilike(f"%{q}%")
            | Device.imei.ilike(f"%{q}%")
        )
    devices = query.order_by(Device.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    return devices


@router.post("", response_model=DeviceResponse, status_code=201)
def create_device(
    payload: DeviceCreate,
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

    device = Device(
        company_id=user.company_id,
        customer_id=payload.customer_id,
        category=payload.category,
        brand=payload.brand,
        model=payload.model,
        color=payload.color,
        imei=payload.imei,
        serial_number=payload.serial_number,
        physical_condition=payload.physical_condition,
        notes=payload.notes,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    device = (
        db.query(Device)
        .filter(
            Device.id == device_id,
            Device.company_id == user.company_id,
            Device.deleted_at.is_(None),
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Aparelho não encontrado")
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: uuid.UUID,
    payload: DeviceUpdate,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    device = (
        db.query(Device)
        .filter(
            Device.id == device_id,
            Device.company_id == user.company_id,
            Device.deleted_at.is_(None),
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Aparelho não encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)
    return device


@router.delete("/{device_id}")
def delete_device(
    device_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    from datetime import datetime, timezone

    device = (
        db.query(Device)
        .filter(
            Device.id == device_id,
            Device.company_id == user.company_id,
            Device.deleted_at.is_(None),
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Aparelho não encontrado")

    device.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Aparelho removido"}


@router.get("/{device_id}/service-orders")
def list_device_service_orders(
    device_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    from app.models.service_order import ServiceOrder

    device = (
        db.query(Device)
        .filter(
            Device.id == device_id,
            Device.company_id == user.company_id,
            Device.deleted_at.is_(None),
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Aparelho não encontrado")

    orders = (
        db.query(ServiceOrder)
        .filter(
            ServiceOrder.device_id == device_id,
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
