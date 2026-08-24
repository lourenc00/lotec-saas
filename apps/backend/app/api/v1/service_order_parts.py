import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_company_access, CurrentUser
from app.models.service_order import ServiceOrder
from app.models.service_order_part import ServiceOrderPart
from app.schemas.service_order import (
    ServiceOrderPartCreate,
    ServiceOrderPartUpdate,
    ServiceOrderPartResponse,
)

router = APIRouter()


def _get_order_or_404(db: Session, order_id: uuid.UUID, company_id: uuid.UUID) -> ServiceOrder:
    so = (
        db.query(ServiceOrder)
        .filter(
            ServiceOrder.id == order_id,
            ServiceOrder.company_id == company_id,
            ServiceOrder.deleted_at.is_(None),
        )
        .first()
    )
    if not so:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
    return so


@router.get("/{order_id}/parts", response_model=list[ServiceOrderPartResponse])
def list_parts(
    order_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    _get_order_or_404(db, order_id, user.company_id)
    items = (
        db.query(ServiceOrderPart)
        .filter(
            ServiceOrderPart.service_order_id == order_id,
            ServiceOrderPart.company_id == user.company_id,
        )
        .order_by(ServiceOrderPart.created_at)
        .all()
    )
    return items


@router.post("/{order_id}/parts", response_model=ServiceOrderPartResponse, status_code=201)
def create_part(
    order_id: uuid.UUID,
    payload: ServiceOrderPartCreate,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    _get_order_or_404(db, order_id, user.company_id)
    total_price = payload.quantity * payload.unit_price
    part = ServiceOrderPart(
        company_id=user.company_id,
        service_order_id=order_id,
        description=payload.description,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        total_price=total_price,
    )
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


@router.put("/{order_id}/parts/{part_id}", response_model=ServiceOrderPartResponse)
def update_part(
    order_id: uuid.UUID,
    part_id: uuid.UUID,
    payload: ServiceOrderPartUpdate,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    _get_order_or_404(db, order_id, user.company_id)
    part = (
        db.query(ServiceOrderPart)
        .filter(
            ServiceOrderPart.id == part_id,
            ServiceOrderPart.service_order_id == order_id,
            ServiceOrderPart.company_id == user.company_id,
        )
        .first()
    )
    if not part:
        raise HTTPException(status_code=404, detail="Peça não encontrada")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(part, field, value)

    if payload.quantity is not None or payload.unit_price is not None:
        part.total_price = part.quantity * part.unit_price

    db.commit()
    db.refresh(part)
    return part


@router.delete("/{order_id}/parts/{part_id}")
def delete_part(
    order_id: uuid.UUID,
    part_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    _get_order_or_404(db, order_id, user.company_id)
    part = (
        db.query(ServiceOrderPart)
        .filter(
            ServiceOrderPart.id == part_id,
            ServiceOrderPart.service_order_id == order_id,
            ServiceOrderPart.company_id == user.company_id,
        )
        .first()
    )
    if not part:
        raise HTTPException(status_code=404, detail="Peça não encontrada")

    db.delete(part)
    db.commit()
    return {"message": "Peça removida"}
