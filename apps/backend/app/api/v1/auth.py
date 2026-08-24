import uuid
import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.deps import get_current_user, CurrentUser
from app.models.user import User
from app.models.company_user import CompanyUser
from app.models.company import Company
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado",
        )

    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        status="ACTIVE",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada",
        )

    company_link = (
        db.query(CompanyUser)
        .filter(CompanyUser.user_id == user.id, CompanyUser.status == "ACTIVE")
        .first()
    )

    token_data = {
        "sub": str(user.id),
        "company_id": str(company_link.company_id) if company_link else None,
        "role": company_link.role if company_link else None,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    payload_data = decode_token(payload.refresh_token)
    if payload_data is None or payload_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        )

    user_id = payload_data.get("sub")
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if user is None or user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inválido",
        )

    company_link = (
        db.query(CompanyUser)
        .filter(CompanyUser.user_id == user.id, CompanyUser.status == "ACTIVE")
        .first()
    )

    token_data = {
        "sub": str(user.id),
        "company_id": str(company_link.company_id) if company_link else None,
        "role": company_link.role if company_link else None,
    }

    new_access = create_access_token(token_data)
    new_refresh = create_refresh_token(token_data)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
    )


@router.post("/logout")
def logout(user: CurrentUser = Depends(get_current_user)):
    return {"message": "Logout realizado com sucesso"}


@router.get("/me")
def me(user: CurrentUser = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "is_super_admin": user.is_super_admin,
        "company_id": str(user.company_id) if user.company_id else None,
        "role": user.role,
    }


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user:
        token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        print(f"RESET TOKEN (dev only): {token}")
    return {"message": "Se o e-mail existir, você receberá um link de redefinição"}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    return {"message": "Senha redefinida com sucesso"}
