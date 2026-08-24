from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin, require_company_access, CurrentUser
from app.models.company import Company
from app.models.company_user import CompanyUser
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse

router = APIRouter()


@router.get("", response_model=CompanyResponse)
def get_company(
    user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == user.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return company


@router.put("", response_model=CompanyResponse)
def update_company(
    payload: CompanyUpdate,
    user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == user.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return company


@router.post("", response_model=CompanyResponse, status_code=201)
def create_company(
    payload: CompanyCreate,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(CompanyUser)
        .filter(CompanyUser.user_id == user.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Usuário já está vinculado a uma empresa",
        )

    company = Company(
        name=payload.name,
        legal_name=payload.legal_name,
        document=payload.document,
        email=payload.email,
        phone=payload.phone,
        status="ACTIVE",
    )
    db.add(company)
    db.flush()

    company_user = CompanyUser(
        company_id=company.id,
        user_id=user.id,
        role="ADMIN",
        status="ACTIVE",
        joined_at=company.created_at,
    )
    db.add(company_user)
    db.commit()
    db.refresh(company)
    return company
