from fastapi import APIRouter

from app.api.v1 import (
    auth,
    company,
    users,
    customers,
    devices,
    service_orders,
    service_order_services,
    service_order_parts,
    plans,
    search,
    subscription,
    dashboard,
    reports,
    admin,
    photos,
    exports,
    portal,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(company.router, prefix="/company", tags=["company"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(subscription.router, prefix="/subscription", tags=["subscription"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(
    service_order_services.router, prefix="/service-orders", tags=["service-order-services"]
)
api_router.include_router(
    service_order_parts.router, prefix="/service-orders", tags=["service-order-parts"]
)
api_router.include_router(
    service_orders.router, prefix="/service-orders", tags=["service-orders"]
)
api_router.include_router(photos.router, prefix="/service-orders", tags=["photos"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
api_router.include_router(portal.router, prefix="/portal", tags=["portal"])
