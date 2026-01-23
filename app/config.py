"""
Configuración de la aplicación FreshKeep - CORS CORREGIDO
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
    
    # 🔥 CORS - SOLUCIÓN AL PROBLEMA
    @property
    def allowed_origins(self) -> list:
        """
        Devuelve lista de orígenes permitidos.
        En desarrollo permite todo (*), en producción solo dominios específicos.
        """
        # Si estamos en desarrollo local
        if self.DEBUG:
            return ["*"]
        
        # En producción, lista exacta de dominios
        return [
            "http://localhost:3000",
            "http://localhost:8000",
            "https://nowasteapp.netlify.app",  # ✅ TU FRONTEND EN NETLIFY
            "https://plataforma-nowaste.onrender.com",  # ✅ TU BACKEND
        ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia única de configuración
settings = Settings()