from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.plan import Plan

router = APIRouter()


@router.get("")
def list_plans(db: Session = Depends(get_db)):
    plans = (
        db.query(Plan)
        .filter(Plan.active == True)
        .order_by(Plan.display_order)
        .all()
    )
    return [
        {
            "id": str(p.id),
            "code": p.code,
            "name": p.name,
            "description": p.description,
            "price_monthly": float(p.price_monthly),
            "currency": p.currency,
            "features": [
                {
                    "code": pf.feature.code,
                    "name": pf.feature.name,
                    "value_type": pf.feature.value_type,
                    "bool_value": pf.bool_value,
                    "int_value": pf.int_value,
                    "string_value": pf.string_value,
                }
                for pf in p.features
            ],
        }
        for p in plans
    ]


@router.get("/{plan_code}")
def get_plan(plan_code: str, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.code == plan_code, Plan.active == True).first()
    if not plan:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    return {
        "id": str(plan.id),
        "code": plan.code,
        "name": plan.name,
        "description": plan.description,
        "price_monthly": float(plan.price_monthly),
        "currency": plan.currency,
        "features": [
            {
                "code": pf.feature.code,
                "name": pf.feature.name,
                "value_type": pf.feature.value_type,
                "bool_value": pf.bool_value,
                "int_value": pf.int_value,
                "string_value": pf.string_value,
            }
            for pf in plan.features
        ],
    }
