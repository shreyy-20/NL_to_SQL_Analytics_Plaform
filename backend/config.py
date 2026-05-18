"""
Configuration management for KrishiQuery
Loads environment variables and provides typed settings
"""

from typing import List, Optional
from pydantic import Field, validator
import os
from dotenv import load_dotenv

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel

    class BaseSettings(BaseModel):
        """
        Lightweight fallback when pydantic-settings is unavailable.
        It reads values from environment variables populated by python-dotenv.
        """

        def __init__(self, **data):
            env_data = {}
            for name, field in self.__class__.model_fields.items():
                env_key = name
                extra = field.json_schema_extra or {}
                if "env" in extra and isinstance(extra["env"], str):
                    env_key = extra["env"]

                if env_key in os.environ and name not in data:
                    env_data[name] = os.environ[env_key]

            env_data.update(data)
            super().__init__(**env_data)

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "KrishiQuery"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=40, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    
    # API Security
    API_KEY: str = Field(..., env="API_KEY")
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Bhashini API
    BHASHINI_API_KEY: Optional[str] = Field(None, env="BHASHINI_API_KEY")
    BHASHINI_API_URL: str = Field(default="https://api.bhashini.gov.in", env="BHASHINI_API_URL")
    BHASHINI_USER_ID: Optional[str] = Field(None, env="BHASHINI_USER_ID")
    
    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = Field(None, env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(None, env="TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = Field(None, env="TWILIO_PHONE_NUMBER")
    
    # AI Models
    INTENT_MODEL_PATH: str = Field(default="models/distilbert-intent-classifier", env="INTENT_MODEL_PATH")
    SQL_MODEL_PATH: str = Field(default="models/codellama-sql-generator", env="SQL_MODEL_PATH")
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", env="EMBEDDING_MODEL")
    
    # Rate Limiting
    RATE_LIMIT_PER_PHONE: int = Field(default=10, env="RATE_LIMIT_PER_PHONE")
    RATE_LIMIT_WINDOW_MINUTES: int = Field(default=1, env="RATE_LIMIT_WINDOW_MINUTES")
    
    # Cache
    REDIS_URL: Optional[str] = Field(None, env="REDIS_URL")
    CACHE_TTL_SECONDS: int = Field(default=300, env="CACHE_TTL_SECONDS")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/krishiquery.log", env="LOG_FILE")
    
    # CORS
    # In backend/config.py, change:
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    ALLOWED_HOSTS: List[str] = Field(default=["localhost", "127.0.0.1"], env="ALLOWED_HOSTS")
    
    # Feature Flags
    ENABLE_VOICE: bool = Field(default=True, env="ENABLE_VOICE")
    ENABLE_WEATHER: bool = Field(default=True, env="ENABLE_WEATHER")
    ENABLE_IVR: bool = Field(default=False, env="ENABLE_IVR")
    
    # External APIs
    WEATHER_API_KEY: Optional[str] = Field(None, env="WEATHER_API_KEY")
    MANDI_API_URL: Optional[str] = Field(None, env="MANDI_API_URL")
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # If it looks like JSON array, parse it
            if v.startswith('['):
                import json
                return json.loads(v)
            # Otherwise treat as single origin
            return [origin.strip() for origin in v.split(',')]
        return v

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list"""
        if isinstance(v, str):
            if v.startswith('['):
                import json
                return json.loads(v)
            return [host.strip() for host in v.split(',')]
        return v

    @validator("DEBUG", pre=True)
    def parse_debug_flag(cls, v):
        """Allow common non-boolean DEBUG env values."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            normalized = v.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "prod", "production"}:
                return False
        return bool(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Create global settings instance
settings = Settings()

# Validate critical settings based on environment
if settings.ENVIRONMENT == "production":
    assert settings.API_KEY != "your_secure_api_key_for_development", \
        "Please change API_KEY in production"
    assert settings.JWT_SECRET_KEY != "your_jwt_secret_key_min_32_chars", \
        "Please change JWT_SECRET_KEY in production"
    assert settings.DATABASE_URL != "postgresql://krishiquery_user:secure_password@localhost:5432/krishiquery_db", \
        "Please update DATABASE_URL for production"

# Create necessary directories
os.makedirs("logs", exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

def get_settings() -> Settings:
    """Dependency to get settings"""
    return settings
