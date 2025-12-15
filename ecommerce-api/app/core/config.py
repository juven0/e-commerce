
"""
Configuration centrale de l'application E-commerce API
Gestion des variables d'environnement avec Pydantic Settings
"""

from typing import List, Optional
from pydantic import field_validator, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration globale de l'application
    Charge automatiquement les variables depuis .env
    """
    
    # ===== Application =====
    APP_NAME: str = "E-commerce API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # ===== Server =====
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # ===== Database =====
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str = "ecommerce_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    @property
    def DATABASE_URL(self) -> str:
        """Génère l'URL de connexion MySQL avec asyncmy"""
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """URL de connexion synchrone (pour Alembic migrations)"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # ===== Security & JWT =====
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Valide que la clé secrète est suffisamment longue"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY doit contenir au moins 32 caractères")
        return v
    
    # ===== CORS =====
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    ALLOWED_METHODS: str = "GET,POST,PUT,DELETE,PATCH"
    ALLOWED_HEADERS: str = "*"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Convertit la chaîne ALLOWED_ORIGINS en liste"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def CORS_METHODS(self) -> List[str]:
        """Convertit la chaîne ALLOWED_METHODS en liste"""
        return [method.strip() for method in self.ALLOWED_METHODS.split(",")]
    
    # ===== Redis Cache =====
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # secondes
    
    @property
    def REDIS_URL(self) -> str:
        """Génère l'URL Redis"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ===== Email =====
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_FROM_NAME: str = "E-commerce"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    
    # ===== File Upload =====
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,gif,webp"
    
    @property
    def ALLOWED_IMAGE_EXTENSIONS(self) -> List[str]:
        """Liste des extensions autorisées"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    # ===== Payment Gateways =====
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLIC_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    PAYPAL_MODE: str = "sandbox"
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    
    # ===== Rate Limiting =====
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # ===== Pagination =====
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # ===== Logging =====
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # ===== Sentry =====
    SENTRY_DSN: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    # ===== Frontend =====
    FRONTEND_URL: str = "http://localhost:3000"
    
    # ===== Admin =====
    ADMIN_EMAIL: EmailStr
    ADMIN_PASSWORD: str
    
    # ===== Celery =====
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # ===== Session =====
    SESSION_SECRET_KEY: str
    SESSION_MAX_AGE: int = 86400  # 24h
    
    # ===== Testing =====
    TEST_DATABASE_URL: Optional[str] = None
    
    # Configuration Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def is_production(self) -> bool:
        """Vérifie si on est en production"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Vérifie si on est en développement"""
        return self.ENVIRONMENT.lower() == "development"


# Instance globale des settings
settings = Settings()


# Fonction helper pour faciliter l'import
def get_settings() -> Settings:
    """
    Retourne l'instance des settings
    Utile pour l'injection de dépendances FastAPI
    """
    return settings