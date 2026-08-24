import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_company_access, CurrentUser
from app.models.service_order import ServiceOrder
from app.models.service_order_service import ServiceOrderService
from app.schemas.service_order import (
    ServiceOrderServiceCreate,
    ServiceOrderServiceUpdate,
    ServiceOrderServiceResponse,
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


@router.get("/{order_id}/services", response_model=list[ServiceOrderServiceResponse])
def list_services(
    order_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    _get_order_or_404(db, order_id, user.company_id)
    items = (
        db.query(ServiceOrderService)
        .filter(
            ServiceOrderService.service_order_id == order_id,
            ServiceOrderService.company_id == user.company_id,
        )
        .order_by(ServiceOrderService.created_at)
        .all()
    )
    return items


@router.post("/{order_id}/services", response_model=ServiceOrderServiceResponse, status_code=201)
def create_service(
    order_id: uuid.UUID,
    payload: ServiceOrderServiceCreate,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    _get_order_or_404(db, order_id, user.company_id)
    total_price = payload.quantity * payload.unit_price
    svc = ServiceOrderService(
        company_id=user.company_id,
        service_order_id=order_id,
        description=payload.description,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        total_price=total_price,
    )
    db.add(svc)
    db.commit()
    db.refresh(svc)
    return svc


@router.put("/{order_id}/services/{service_id}", response_model=ServiceOrderServiceResponse)
def update_service(
    order_id: uuid.UUID,
    service_id: uuid.UUID,
    payload: ServiceOrderServiceUpdate,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    _get_order_or_404(db, order_id, user.company_id)
    svc = (
        db.query(ServiceOrderService)
        .filter(
            ServiceOrderService.id == service_id,
            ServiceOrderService.service_order_id == order_id,
            ServiceOrderService.company_id == user.company_id,
        )
        .first()
    )
    if not svc:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(svc, field, value)

    if payload.quantity is not None or payload.unit_price is not None:
        svc.total_price = svc.quantity * svc.unit_price

    db.commit()
    db.refresh(svc)
    return svc


@router.delete("/{order_id}/services/{service_id}")
def delete_service(
    order_id: uuid.UUID,
    service_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    _get_order_or_404(db, order_id, user.company_id)
    svc = (
        db.query(ServiceOrderService)
        .filter(
            ServiceOrderService.id == service_id,
            ServiceOrderService.service_order_id == order_id,
            ServiceOrderService.company_id == user.company_id,
        )
        .first()
    )
    if not svc:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    db.delete(svc)
    db.commit()
    return {"message": "Serviço removido"}
