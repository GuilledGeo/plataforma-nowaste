"""
Configuración de la base de datos
Similar a la configuración de BD en Django
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Crear engine de SQLAlchemy
# Para SQLite usamos check_same_thread=False
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# SessionLocal será nuestra "sesión" de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base será la clase base para nuestros modelos (como models.Model en Django)
Base = declarative_base()


def get_db():
    """
    Dependency para obtener una sesión de base de datos
    Se usa con Depends() en FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
