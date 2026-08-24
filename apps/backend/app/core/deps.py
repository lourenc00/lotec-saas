import uuid
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.models.company_user import CompanyUser

security = HTTPBearer()


@dataclass
class CurrentUser:
    id: uuid.UUID
    email: str
    name: str
    is_super_admin: bool
    company_id: uuid.UUID | None = None
    role: str | None = None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> CurrentUser:
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if user is None or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
        )

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )

    company_id_str = payload.get("company_id")
    role = payload.get("role")

    return CurrentUser(
        id=user.id,
        email=user.email,
        name=user.name,
        is_super_admin=user.is_super_admin,
        company_id=uuid.UUID(company_id_str) if company_id_str else None,
        role=role,
    )


def require_company_access(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.is_super_admin:
        return user
    if user.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não está vinculado a uma empresa",
        )
    return user


def require_admin(user: CurrentUser = Depends(require_company_access)) -> CurrentUser:
    if user.is_super_admin:
        return user
    if user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem acessar este recurso",
        )
    return user


def require_super_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if not user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito ao Super Admin",
        )
    return user


class RequireFeature:
    def __init__(self, feature_code: str):
        self.feature_code = feature_code

    def __call__(
        self,
        user: CurrentUser = Depends(require_company_access),
        db: Session = Depends(get_db),
    ) -> CurrentUser:
        from app.services.plan_evaluator import PlanEvaluator

        evaluator = PlanEvaluator(db, user.company_id)
        evaluator.require(self.feature_code)
        return user
