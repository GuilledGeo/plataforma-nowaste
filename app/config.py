"""
Configuración de la aplicación FreshKeep
Similar a settings.py en Django
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic"""
    
    # Información de la App
    APP_NAME: str = "FreshKeep"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # Base de Datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./freshkeep.db")    
    # Seguridad - JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia única de configuración
settings = Settings()
