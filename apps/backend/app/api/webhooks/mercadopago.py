from datetime import datetime, timezone

from fastapi import APIRouter, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.mercadopago.client import mp_client
from app.models.subscription import WebhookEvent
from app.services.subscription import SubscriptionService

router = APIRouter()


@router.post("/mercadopago")
async def mercadopago_webhook(request: Request):
    body = await request.body()
    headers = dict(request.headers)

    db: Session = next(get_db())

    try:
        signature_valid = mp_client.validate_webhook_signature(body, headers)

        event_type = None
        action = None
        resource_id = None

        try:
            data = await request.json()
            event_type = data.get("type") or data.get("action")
            action = data.get("action")
            resource = data.get("resource", "")
            if "/" in resource:
                resource_id = resource.split("/")[-1]
        except Exception:
            pass

        event_key = f"mp_{headers.get('x-request-id', '')}_{event_type}_{resource_id}"

        existing = db.query(WebhookEvent).filter(WebhookEvent.event_key == event_key).first()
        if existing:
            return Response(status_code=200)

        event = WebhookEvent(
            provider="mercadopago",
            event_key=event_key,
            event_type=event_type,
            action=action,
            resource_id=resource_id,
            signature_valid=signature_valid,
            payload=data if 'data' in dir() else None,
            headers_sanitized={
                "x-request-id": headers.get("x-request-id"),
                "x-signature": "present" if headers.get("x-signature") else None,
            },
            processing_status="RECEIVED",
            received_at=datetime.now(timezone.utc),
        )
        db.add(event)
        db.flush()

        if not signature_valid:
            event.processing_status = "IGNORED"
            event.processing_error = "Invalid signature"
            db.commit()
            return Response(status_code=200)

        event.processing_status = "PROCESSING"
        db.commit()

        try:
            sub_service = SubscriptionService(db)
            sub_service.process_webhook(event_type, resource_id, {})
            event.processing_status = "PROCESSED"
            event.processed_at = datetime.now(timezone.utc)
        except Exception as e:
            event.processing_status = "FAILED"
            event.processing_error = str(e)[:500]

        db.commit()
        return Response(status_code=200)

    except Exception as e:
        return Response(status_code=200)
    finally:
        db.close()
