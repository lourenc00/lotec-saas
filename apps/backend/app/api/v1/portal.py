import uuid
import secrets
import hashlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.service_order import ServiceOrder
from app.models.customer import Customer
from app.models.device import Device

router = APIRouter()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@router.get("/{tracking_token}")
def portal_tracking(tracking_token: str, db: Session = Depends(get_db)):
    token_hash = _hash_token(tracking_token)
    so = (
        db.query(ServiceOrder)
        .filter(ServiceOrder.public_tracking_token_hash == token_hash)
        .first()
    )
    if not so:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

    customer = db.query(Customer).filter(Customer.id == so.customer_id).first()
    device = db.query(Device).filter(Device.id == so.device_id).first()

    history = [
        {
            "status": h.new_status,
            "date": h.created_at.isoformat(),
            "notes": h.notes,
        }
        for h in sorted(so.status_history, key=lambda x: x.created_at)
    ]

    return {
        "os_number": so.os_number,
        "status": so.status,
        "customer_name": customer.name if customer else None,
        "device": f"{device.brand} {device.model}" if device else None,
        "entry_at": so.entry_at.isoformat() if so.entry_at else None,
        "estimated_delivery_at": so.estimated_delivery_at.isoformat() if so.estimated_delivery_at else None,
        "history": history,
    }


@router.post("/{order_id}/tracking-token")
def generate_tracking_token(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    so = db.query(ServiceOrder).filter(ServiceOrder.id == order_id).first()
    if not so:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

    token = secrets.token_urlsafe(32)
    so.public_tracking_token_hash = _hash_token(token)
    db.commit()

    return {"tracking_token": token, "tracking_url": f"/r/{token}"}
