import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.plan import Plan, Feature, PlanFeature


def seed_plans_and_features(db: Session):
    existing = db.query(Plan).first()
    if existing:
        return

    basic = Plan(
        code="basic",
        name="Básico",
        description="Para quem está começando",
        price_monthly=29.90,
        currency="BRL",
        active=True,
        display_order=1,
    )
    professional = Plan(
        code="professional",
        name="Profissional",
        description="Para quem quer crescer",
        price_monthly=49.90,
        currency="BRL",
        active=True,
        display_order=2,
    )
    premium = Plan(
        code="premium",
        name="Premium",
        description="Para quem quer tudo",
        price_monthly=79.90,
        currency="BRL",
        active=True,
        display_order=3,
    )

    db.add_all([basic, professional, premium])
    db.flush()

    features_data = [
        ("can_manage_users", "Gerenciar Usuários", "boolean"),
        ("can_view_reports", "Visualizar Relatórios", "boolean"),
        ("can_export_data", "Exportar Dados", "boolean"),
        ("can_upload_photos", "Enviar Fotos", "boolean"),
        ("can_access_customer_portal", "Portal do Cliente", "boolean"),
        ("can_use_advanced_dashboard", "Dashboard Avançado", "boolean"),
        ("can_use_advanced_permissions", "Permissões Avançadas", "boolean"),
        ("max_users", "Máximo de Usuários", "integer"),
        ("max_storage_mb", "Armazenamento (MB)", "integer"),
    ]

    feature_map = {}
    for code, name, vtype in features_data:
        f = Feature(code=code, name=name, value_type=vtype)
        db.add(f)
        db.flush()
        feature_map[code] = f

    plan_features = {
        "basic": {
            "can_manage_users": False,
            "can_view_reports": False,
            "can_export_data": False,
            "can_upload_photos": False,
            "can_access_customer_portal": False,
            "can_use_advanced_dashboard": False,
            "can_use_advanced_permissions": False,
            "max_users": 1,
            "max_storage_mb": 100,
        },
        "professional": {
            "can_manage_users": True,
            "can_view_reports": True,
            "can_export_data": False,
            "can_upload_photos": False,
            "can_access_customer_portal": False,
            "can_use_advanced_dashboard": True,
            "can_use_advanced_permissions": True,
            "max_users": 5,
            "max_storage_mb": 500,
        },
        "premium": {
            "can_manage_users": True,
            "can_view_reports": True,
            "can_export_data": True,
            "can_upload_photos": True,
            "can_access_customer_portal": True,
            "can_use_advanced_dashboard": True,
            "can_use_advanced_permissions": True,
            "max_users": 20,
            "max_storage_mb": 5000,
        },
    }

    plan_map = {"basic": basic, "professional": professional, "premium": premium}

    for plan_code, features in plan_features.items():
        plan = plan_map[plan_code]
        for feature_code, value in features.items():
            feature = feature_map[feature_code]
            pf = PlanFeature(
                plan_id=plan.id,
                feature_id=feature.id,
                bool_value=value if isinstance(value, bool) else None,
                int_value=value if isinstance(value, int) else None,
            )
            db.add(pf)

    db.commit()
    print("Seed completed: plans and features created")
