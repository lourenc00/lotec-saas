"""Create initial tables

Revision ID: 001
Revises:
Create Date: 2026-08-19
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON, INET

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="ACTIVE"),
        sa.Column("is_super_admin", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_status", "users", ["status"])

    op.create_table(
        "companies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("legal_name", sa.String(180), nullable=True),
        sa.Column("document", sa.String(30), nullable=True),
        sa.Column("email", sa.String(254), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("whatsapp", sa.String(30), nullable=True),
        sa.Column("address_line", sa.String(255), nullable=True),
        sa.Column("address_number", sa.String(30), nullable=True),
        sa.Column("address_extra", sa.String(100), nullable=True),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("zip_code", sa.String(12), nullable=True),
        sa.Column("logo_key", sa.String(500), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="ACTIVE"),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="America/Sao_Paulo"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_companies_status", "companies", ["status"])
    op.create_index("idx_companies_document", "companies", ["document"])

    op.create_table(
        "company_users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(30), nullable=False, server_default="ADMIN"),
        sa.Column("status", sa.String(30), nullable=False, server_default="ACTIVE"),
        sa.Column("invited_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("company_id", "user_id", name="uq_company_user"),
    )
    op.create_index("idx_company_users_company_id", "company_users", ["company_id"])
    op.create_index("idx_company_users_user_id", "company_users", ["user_id"])

    op.create_table(
        "company_counters",
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), primary_key=True),
        sa.Column("next_os_number", sa.BigInteger, nullable=False, server_default=sa.text("1")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "plans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("price_monthly", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="BRL"),
        sa.Column("mercadopago_plan_id", sa.String(255), nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("display_order", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "features",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(100), unique=True, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("value_type", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "plan_features",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("plan_id", UUID(as_uuid=True), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("feature_id", UUID(as_uuid=True), sa.ForeignKey("features.id"), nullable=False),
        sa.Column("bool_value", sa.Boolean, nullable=True),
        sa.Column("int_value", sa.Integer, nullable=True),
        sa.Column("string_value", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("plan_id", "feature_id", name="uq_plan_feature"),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("plan_id", UUID(as_uuid=True), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False, server_default="mercadopago"),
        sa.Column("provider_subscription_id", sa.String(255), nullable=True),
        sa.Column("provider_payer_id", sa.String(255), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="TRIAL"),
        sa.Column("provider_status", sa.String(100), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_billing_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("past_due_since", sa.DateTime(timezone=True), nullable=True),
        sa.Column("grace_period_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_subscriptions_company", "subscriptions", ["company_id"])

    op.create_table(
        "webhook_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("event_key", sa.String(255), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=True),
        sa.Column("action", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("signature_valid", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("payload", JSON, nullable=True),
        sa.Column("headers_sanitized", JSON, nullable=True),
        sa.Column("processing_status", sa.String(30), nullable=False),
        sa.Column("processing_error", sa.Text, nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("provider", "event_key", name="uq_webhook_event"),
    )

    op.create_table(
        "payments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("subscription_id", UUID(as_uuid=True), sa.ForeignKey("subscriptions.id"), nullable=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("provider_payment_id", sa.String(255), nullable=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("provider_status", sa.String(100), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="BRL"),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "customers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("document", sa.String(30), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("whatsapp", sa.String(30), nullable=True),
        sa.Column("email", sa.String(254), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_customers_company", "customers", ["company_id"])

    op.create_table(
        "devices",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("customer_id", UUID(as_uuid=True), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("brand", sa.String(100), nullable=True),
        sa.Column("model", sa.String(150), nullable=False),
        sa.Column("color", sa.String(80), nullable=True),
        sa.Column("imei", sa.String(30), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("physical_condition", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_devices_company", "devices", ["company_id"])
    op.create_index("idx_devices_customer", "devices", ["customer_id"])

    op.create_table(
        "service_orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("os_number", sa.BigInteger, nullable=False),
        sa.Column("customer_id", UUID(as_uuid=True), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("device_id", UUID(as_uuid=True), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("responsible_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="RECEIVED"),
        sa.Column("entry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_delivery_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completion_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("problem_reported", sa.Text, nullable=False),
        sa.Column("service_requested", sa.Text, nullable=True),
        sa.Column("diagnosis", sa.Text, nullable=True),
        sa.Column("service_performed_summary", sa.Text, nullable=True),
        sa.Column("internal_notes", sa.Text, nullable=True),
        sa.Column("customer_notes", sa.Text, nullable=True),
        sa.Column("estimated_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("approved_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("final_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("payment_status", sa.String(30), nullable=True),
        sa.Column("public_tracking_token_hash", sa.String(255), nullable=True),
        sa.Column("created_by_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_by_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("company_id", "os_number", name="uq_so_company_number"),
    )
    op.create_index("idx_service_orders_company", "service_orders", ["company_id"])
    op.create_index("idx_service_orders_company_status", "service_orders", ["company_id", "status"])

    op.create_table(
        "service_order_status_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("service_order_id", UUID(as_uuid=True), sa.ForeignKey("service_orders.id"), nullable=False),
        sa.Column("previous_status", sa.String(30), nullable=True),
        sa.Column("new_status", sa.String(30), nullable=False),
        sa.Column("changed_by_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_so_history_order", "service_order_status_history", ["service_order_id"])

    op.create_table(
        "service_order_services",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("service_order_id", UUID(as_uuid=True), sa.ForeignKey("service_orders.id"), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False, server_default=sa.text("1")),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "service_order_parts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("service_order_id", UUID(as_uuid=True), sa.ForeignKey("service_orders.id"), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False, server_default=sa.text("1")),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("request_id", sa.String(100), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=True),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=True),
        sa.Column("old_data", JSON, nullable=True),
        sa.Column("new_data", JSON, nullable=True),
        sa.Column("ip_address", INET, nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
    )
    op.create_index("idx_refresh_tokens_user", "refresh_tokens", ["user_id"])

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("password_reset_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("audit_logs")
    op.drop_table("service_order_parts")
    op.drop_table("service_order_services")
    op.drop_table("service_order_status_history")
    op.drop_table("service_orders")
    op.drop_table("devices")
    op.drop_table("customers")
    op.drop_table("payments")
    op.drop_table("webhook_events")
    op.drop_table("subscriptions")
    op.drop_table("plan_features")
    op.drop_table("features")
    op.drop_table("plans")
    op.drop_table("company_counters")
    op.drop_table("company_users")
    op.drop_table("companies")
    op.drop_table("users")
