import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Information
    PROJECT_NAME: str = "AvalancheVision"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    FRONTEND_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    API_KEY: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    # Copernicus Credentials
    CDSE_CLIENT_ID: str = ""
    CDSE_CLIENT_SECRET: str = ""
    CDSE_TOKEN_URL: str = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    CDSE_STAC_URL: str = "https://catalogue.dataspace.copernicus.eu/stac"
    CDSE_ODATA_URL: str = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

    # Directory Paths (Relative to Root)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_RAW_DIR: Path = BASE_DIR / "data" / "raw"
    DATA_PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
    MODELS_DIR: Path = BASE_DIR / "ml" / "models"

    # Default SAR Search Constraints
    DEFAULT_SATELLITE: str = "SENTINEL-1"
    DEFAULT_SENSOR_MODE: str = "IW"
    DEFAULT_PRODUCT_TYPE: str = "GRD"
    DEFAULT_POLARIZATIONS: list[str] = ["VV", "VH"]

    # Database Settings
    POSTGRES_USER: str = "avalanche"
    POSTGRES_PASSWORD: str = "avalanche_secure_pass"
    POSTGRES_DB: str = "avalanchevision_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    USE_SQLITE: bool = False

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    @property
    def resolved_celery_broker_url(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def resolved_celery_result_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def create_directories(self) -> None:
        """Ensures required local runtime data directories exist."""
        self.DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.create_directories()