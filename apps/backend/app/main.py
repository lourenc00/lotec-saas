from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import time

from app.core.config import settings
from app.api.v1.router import api_router
from app.api.webhooks.mercadopago import router as webhook_router


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration}ms"
        return response


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        docs_url="/docs" if settings.APP_ENV == "development" else None,
        redoc_url="/redoc" if settings.APP_ENV == "development" else None,
    )

    app.add_middleware(RequestIDMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")
    app.include_router(webhook_router, prefix="/api/webhooks", tags=["webhooks"])

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ready")
    def ready():
        return {"status": "ready"}

    return app


app = create_app()
