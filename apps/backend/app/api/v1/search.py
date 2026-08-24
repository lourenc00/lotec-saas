import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.deps import require_company_access, CurrentUser
from app.models.customer import Customer
from app.models.device import Device
from app.models.service_order import ServiceOrder

router = APIRouter()


@router.get("")
def global_search(
    q: str = Query(..., min_length=1, max_length=100),
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    limit = 20

    customers = (
        db.query(Customer)
        .filter(
            Customer.company_id == user.company_id,
            Customer.deleted_at.is_(None),
            or_(
                Customer.name.ilike(f"%{q}%"),
                Customer.phone.ilike(f"%{q}%"),
                Customer.document.ilike(f"%{q}%"),
                Customer.email.ilike(f"%{q}%"),
            ),
        )
        .limit(limit)
        .all()
    )

    devices = (
        db.query(Device)
        .filter(
            Device.company_id == user.company_id,
            Device.deleted_at.is_(None),
            or_(
                Device.model.ilike(f"%{q}%"),
                Device.brand.ilike(f"%{q}%"),
                Device.imei.ilike(f"%{q}%"),
                Device.serial_number.ilike(f"%{q}%"),
            ),
        )
        .limit(limit)
        .all()
    )

    service_orders = (
        db.query(ServiceOrder)
        .filter(
            ServiceOrder.company_id == user.company_id,
            ServiceOrder.deleted_at.is_(None),
            or_(
                ServiceOrder.problem_reported.ilike(f"%{q}%"),
                ServiceOrder.diagnosis.ilike(f"%{q}%"),
                ServiceOrder.service_performed_summary.ilike(f"%{q}%"),
            ),
        )
        .limit(limit)
        .all()
    )

    return {
        "customers": [
            {"id": str(c.id), "name": c.name, "phone": c.phone}
            for c in customers
        ],
        "devices": [
            {"id": str(d.id), "model": d.model, "brand": d.brand, "imei": d.imei}
            for d in devices
        ],
        "service_orders": [
            {
                "id": str(s.id),
                "os_number": s.os_number,
                "status": s.status,
                "problem_reported": s.problem_reported[:100],
            }
            for s in service_orders
        ],
    }
