import uuid
import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_company_access, CurrentUser
from app.models.service_order import ServiceOrder

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/{order_id}/photos")
async def upload_photo(
    order_id: uuid.UUID,
    file: UploadFile = File(...),
    photo_type: str = "OTHER",
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    so = db.query(ServiceOrder).filter(
        ServiceOrder.id == order_id,
        ServiceOrder.company_id == user.company_id,
        ServiceOrder.deleted_at.is_(None),
    ).first()
    if not so:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Arquivo muito grande (máx 10MB)")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido")

    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    storage_key = f"companies/{user.company_id}/service-orders/{order_id}/{uuid.uuid4()}.{ext}"
    checksum = hashlib.sha256(content).hexdigest()

    try:
        import boto3
        from app.core.config import settings
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        s3.put_object(Bucket=settings.S3_BUCKET, Key=storage_key, Body=content, ContentType=file.content_type)
    except Exception:
        pass

    from app.models.service_order import ServiceOrderPhoto
    photo = ServiceOrderPhoto(
        company_id=user.company_id,
        service_order_id=order_id,
        photo_type=photo_type,
        storage_key=storage_key,
        original_filename=file.filename,
        mime_type=file.content_type,
        file_size=len(content),
        checksum=checksum,
        uploaded_by_user_id=user.id,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return {
        "id": str(photo.id),
        "photo_type": photo.photo_type,
        "storage_key": photo.storage_key,
        "created_at": photo.created_at.isoformat(),
    }


@router.get("/{order_id}/photos")
def list_photos(
    order_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    from app.models.service_order import ServiceOrderPhoto
    photos = db.query(ServiceOrderPhoto).filter(
        ServiceOrderPhoto.service_order_id == order_id,
        ServiceOrderPhoto.company_id == user.company_id,
        ServiceOrderPhoto.deleted_at.is_(None),
    ).all()
    return [
        {
            "id": str(p.id),
            "photo_type": p.photo_type,
            "original_filename": p.original_filename,
            "mime_type": p.mime_type,
            "file_size": p.file_size,
            "created_at": p.created_at.isoformat(),
        }
        for p in photos
    ]


@router.delete("/{order_id}/photos/{photo_id}")
def delete_photo(
    order_id: uuid.UUID,
    photo_id: uuid.UUID,
    user: CurrentUser = Depends(require_company_access),
    db: Session = Depends(get_db),
):
    from app.models.service_order import ServiceOrderPhoto
    from datetime import datetime, timezone
    photo = db.query(ServiceOrderPhoto).filter(
        ServiceOrderPhoto.id == photo_id,
        ServiceOrderPhoto.service_order_id == order_id,
        ServiceOrderPhoto.company_id == user.company_id,
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Foto não encontrada")
    photo.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Foto removida"}
