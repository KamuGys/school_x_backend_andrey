from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str
    db_port: str
    db_user: str
    db_pass: str
    db_name: str

    model_config=SettingsConfigDict(env_file=".env")

settings = Settings()


DB_URL = f"postegres://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"