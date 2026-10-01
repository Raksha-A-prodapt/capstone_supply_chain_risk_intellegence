import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

@dataclass
class Settings:
    BASE_DIR: Path = BASE_DIR
    DATA_PATH: Path = BASE_DIR / os.getenv("DATA_PATH", "data/dataset.csv")
    MODELS_DIR: Path = BASE_DIR / os.getenv("MODELS_DIR", "artifacts/models")
    REPORTS_DIR: Path = BASE_DIR / os.getenv("REPORTS_DIR", "reports")
    DOCS_DIR: Path = BASE_DIR / "knowledge_base" / "documents"

    # Gateway / LLM
    GATEWAY_URL: str = os.getenv("GATEWAY_URL", "https://keygateway1.arshnivlabs.com")
    LEARNER_KEY: str = os.getenv("LEARNER_KEY", "pubatch_trainer")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    LLM_TIMEOUT: int = 25
    SSL_VERIFY: bool = False  # Corporate proxy bypass

    # ML & Anomaly Config
    DELIVERY_RISK_THRESHOLD: float = float(os.getenv("DELIVERY_RISK_THRESHOLD", 0.50))
    ANOMALY_CONTAMINATION: float = float(os.getenv("ANOMALY_CONTAMINATION", 0.03))
    FORECAST_HORIZON_DAYS: int = int(os.getenv("FORECAST_HORIZON_DAYS", 30))
    SAFETY_STOCK_Z: float = float(os.getenv("SAFETY_STOCK_Z", 1.65))  # 95% service level
    LEAD_TIME_ANOMALY_Z: float = 2.5

    # Supplier Risk Weights (Sum to 1.0)
    WEIGHT_LATE_RATE: float = 0.35
    WEIGHT_AVG_DELAY: float = 0.20
    WEIGHT_LEAD_TIME_VAR: float = 0.15
    WEIGHT_ANOMALY_FREQ: float = 0.15
    WEIGHT_ML_PROB: float = 0.15

    # Risk Levels
    RISK_LEVEL_LOW: float = 0.25
    RISK_LEVEL_MEDIUM: float = 0.50
    RISK_LEVEL_HIGH: float = 0.75

    # Server
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 8000))

    # Single-user demo login; override both values in the environment outside local demos.
    AUTH_USERNAME: str = os.getenv("AUTH_USERNAME", "demo@raksha.com")
    AUTH_PASSWORD: str = os.getenv("AUTH_PASSWORD", "SupplyChainDemo2026!")
    SESSION_TTL_SECONDS: int = int(os.getenv("SESSION_TTL_SECONDS", 28800))
    SESSION_COOKIE_SECURE: bool = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"

settings = Settings()
