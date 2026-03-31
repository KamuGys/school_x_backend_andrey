from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "School X Backend"
    app_version: str = "2.0.0"
    environment: str = "dev"

    database_url: str = "sqlite+aiosqlite:///./db.sqlite"

    secret_key: str = "SECRET"
    algorithm: str = "HS256"

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "task-avatars"
    minio_secure: bool = False


settings = Settings()