"""
Configuración de la base de datos
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Usar la URL corregida
database_url = settings.database_url_fixed

# Crear engine de SQLAlchemy
if "sqlite" in database_url:
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL en producción
    engine = create_engine(database_url)

# SessionLocal será nuestra "sesión" de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base será la clase base para nuestros modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obtener una sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()