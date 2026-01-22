"""
Configuración de la aplicación FreshKeep
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic"""
    
    # Información de la App
    APP_NAME: str = "FreshKeep"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    VERSION: str = "1.0.0"
    
    # Base de Datos - Automáticamente usa PostgreSQL en producción
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./freshkeep.db")
    
    # Si es PostgreSQL de Render, ajustar el esquema
    @property
    def database_url_fixed(self):
        url = self.DATABASE_URL
        if url and url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    
    # Seguridad - JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    
    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # CORS - CONFIGURACIÓN CORREGIDA ✅
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "https://nowasteapp.netlify.app",  # ✅ Tu dominio de Netlify
        "https://plataforma-nowaste.onrender.com",  # ✅ Tu backend
        # Añade más dominios específicos aquí si despliegas en otros lugares
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia única de configuración
settings = Settings()