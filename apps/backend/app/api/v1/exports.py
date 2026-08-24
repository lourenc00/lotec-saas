import uuid
import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_company_access, CurrentUser
from app.models.customer import Customer
from app.models.device import Device
from app.models.service_order import ServiceOrder

router = APIRouter()


@router.post("/customers")
def export_customers(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    customers = db.query(Customer).filter(
        Customer.company_id == user.company_id,
        Customer.deleted_at.is_(None),
    ).order_by(Customer.name).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nome", "Documento", "Telefone", "WhatsApp", "E-mail", "Ativo", "Criado em"])
    for c in customers:
        writer.writerow([
            c.name, c.document or "", c.phone or "", c.whatsapp or "",
            c.email or "", "Sim" if c.is_active else "Não",
            c.created_at.strftime("%d/%m/%Y") if c.created_at else "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=clientes_{datetime.now().strftime('%Y%m%d')}.csv"},
    )


@router.post("/service-orders")
def export_service_orders(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    orders = (
        db.query(ServiceOrder)
        .filter(ServiceOrder.company_id == user.company_id, ServiceOrder.deleted_at.is_(None))
        .order_by(ServiceOrder.created_at.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["OS #", "Status", "Problema", "Valor Estimado", "Criado em", "Entregue em"])
    for o in orders:
        writer.writerow([
            o.os_number, o.status, o.problem_reported,
            float(o.estimated_value) if o.estimated_value else "",
            o.created_at.strftime("%d/%m/%Y") if o.created_at else "",
            o.delivery_at.strftime("%d/%m/%Y") if o.delivery_at else "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=os_{datetime.now().strftime('%Y%m%d')}.csv"},
    )
