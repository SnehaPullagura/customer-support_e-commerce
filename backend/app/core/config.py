"""
Application Configuration and Environment Settings.
"""

from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "E-Commerce Customer Support & Resolution Management Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # Security & JWT
    SECRET_KEY: str = "dev-insecure-secret-key-change-in-production-support-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    OTP_EXPIRE_MINUTES: int = 5
    MFA_ISSUER: str = "SupportPlatform"

    # Database
    # Default to async SQLite for out-of-the-box zero-dependency testing, override with PostgreSQL in production
    DATABASE_URL: str = "sqlite+aiosqlite:///./support_platform.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False

    # Redis Cache & PubSub
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False  # Auto-fallback to memory cache if Redis is unavailable

    # Kafka / Event Bus
    KAFKA_BOOTSTRAP_SERVERS: Optional[str] = "localhost:9092"
    KAFKA_ENABLED: bool = False
    EVENT_BUS_DRIVER: str = "in_memory"  # options: 'in_memory', 'redis', 'kafka'

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # SLA Default Policies (in minutes / hours)
    SLA_CRITICAL_FIRST_RESPONSE_MINS: int = 15
    SLA_CRITICAL_RESOLUTION_HOURS: int = 4
    SLA_HIGH_FIRST_RESPONSE_MINS: int = 30
    SLA_HIGH_RESOLUTION_HOURS: int = 8
    SLA_MEDIUM_FIRST_RESPONSE_MINS: int = 60
    SLA_MEDIUM_RESOLUTION_HOURS: int = 24
    SLA_LOW_FIRST_RESPONSE_MINS: int = 120
    SLA_LOW_RESOLUTION_HOURS: int = 48

    # AI & NLP Configuration
    AI_ENABLED: bool = True
    EMBEDDING_DIMENSION: int = 384
    AI_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    AI_CONFIDENCE_THRESHOLD: float = 0.75
    RAG_TOP_K: int = 4
    FRUSTRATION_SCORE_THRESHOLD: float = 65.0

    # Rate Limiting & Idempotency
    RATE_LIMIT_PER_MINUTE: int = 120
    IDEMPOTENCY_EXPIRY_SECONDS: int = 86400  # 24 hours

    # Commerce Adapter
    COMMERCE_ADAPTER_TYPE: str = "mock"  # options: 'mock', 'rest', 'shopify'
    COMMERCE_API_BASE_URL: Optional[str] = "https://api.mock-commerce.internal"
    COMMERCE_API_KEY: Optional[str] = "mock_commerce_key_123"

    # Notification & Storage
    NOTIFICATION_EMAIL_FROM: str = "support@ecommerce-resolution.internal"
    ATTACHMENTS_DIR: str = "./uploads"
    MAX_ATTACHMENT_SIZE_MB: int = 25


settings = Settings()
