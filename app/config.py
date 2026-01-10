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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 🔥 7 días en lugar de 30 minutos
    
    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.netlify.app",
        "https://*.vercel.app",
        "https://plataforma-nowaste.onrender.com",  # 🔥 Añade tu dominio
        "*"  # En producción, quita esto y deja solo dominios específicos
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia única de configuración
settings = Settings()