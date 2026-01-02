from pydantic import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "DCA Management AI Services"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database settings
    MONGODB_URI: str = "mongodb://localhost:27017/dca_platform"
    DATABASE_NAME: str = "dca_platform"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000"
    ]
    
    # AI/ML settings
    MODEL_PATH: str = "models"
    ENABLE_MODEL_CACHING: bool = True
    PREDICTION_BATCH_SIZE: int = 100
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/ai_services.log"
    
    # Performance settings
    MAX_WORKERS: int = 4
    ENABLE_ASYNC_PROCESSING: bool = True
    
    # External services
    BACKEND_API_URL: str = "http://localhost:5000/api"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings() -> Settings:
    return Settings()