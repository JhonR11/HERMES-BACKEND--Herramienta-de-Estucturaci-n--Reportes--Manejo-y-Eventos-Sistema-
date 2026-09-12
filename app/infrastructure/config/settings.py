from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    protocol: str = "http"
    host: str = "localhost"
    port: int = 8000
    base_url: str | None = None

    db_user: str = "app_user"
    db_password: str = "changeme"
    db_host: str = "db"
    db_port: int = 5432
    db_name: str = "reportes_db"
    database_url: str | None = None

    jwt_secret_key: str = "cambia-esta-clave-en-produccion"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    admin_email: str = "admin@institucion.edu.co"
    admin_password: str = "changeme"

    upload_dir: str = "/uploads"
    max_image_bytes: int = 5 * 1024 * 1024
    max_pdf_bytes: int = 10 * 1024 * 1024
    event_expiry_poll_seconds: int = 60
    cors_origins: str = "*"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def resolved_base_url(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")
        return f"{self.protocol}://{self.host}:{self.port}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
