from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_company_access, require_admin, CurrentUser
from app.models.user import User
from app.models.company_user import CompanyUser
from app.schemas.auth import UserCreate, UserResponse

router = APIRouter()


@router.get("", response_model=list[UserResponse])
def list_users(
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    links = (
        db.query(CompanyUser)
        .filter(CompanyUser.company_id == user.company_id, CompanyUser.status == "ACTIVE")
        .all()
    )
    user_ids = [link.user_id for link in links]
    users = (
        db.query(User)
        .filter(User.id.in_(user_ids), User.deleted_at.is_(None))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return users


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    payload: UserCreate,
    user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    new_user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=__import__("app.core.security", fromlist=["hash_password"]).hash_password(payload.password),
        status="ACTIVE",
    )
    db.add(new_user)
    db.flush()

    company_user = CompanyUser(
        company_id=user.company_id,
        user_id=new_user.id,
        role="ATTENDANT",
        status="ACTIVE",
    )
    db.add(company_user)
    db.commit()
    db.refresh(new_user)
    return new_user
