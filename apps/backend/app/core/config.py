from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "Lotec"
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"

    DATABASE_URL: str = "postgresql+psycopg://lotec_user:change_me_in_production@postgres:5432/lotec_db"

    JWT_SECRET: str = "change_me_generate_a_strong_secret"
    JWT_ACCESS_TOKEN_MINUTES: int = 15
    JWT_REFRESH_TOKEN_DAYS: int = 30

    PASSWORD_PEPPER: str = "change_me_pepper_value"

    MERCADOPAGO_ACCESS_TOKEN: str = ""
    MERCADOPAGO_PUBLIC_KEY: str = ""
    MERCADOPAGO_WEBHOOK_SECRET: str = ""

    S3_ENDPOINT: str = "http://minio:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "lotec-files"
    S3_REGION: str = "us-east-1"

    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"
    SUBSCRIPTION_GRACE_PERIOD_DAYS: int = 5

    @property
    def CORS_ALLOWED_ORIGINS_LIST(self) -> list[str]:
        return [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
