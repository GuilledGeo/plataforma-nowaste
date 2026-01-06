"""
Modelo Recipe - Tabla de Recetas
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Recipe(Base):
    """
    Modelo de Receta
    Tabla: recipes
    """
    __tablename__ = "recipes"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información de la receta
    title = Column(String, nullable=False)
    ingredients = Column(Text, nullable=False)  # JSON string con ingredientes
    instructions = Column(Text, nullable=False)
    
    # Metadatos
    prep_time = Column(Integer, nullable=True)  # Minutos
    difficulty = Column(String, default="medium")  # easy, medium, hard
    servings = Column(Integer, default=2)
    
    # AI Generated
    is_ai_generated = Column(Integer, default=1)  # Boolean: 1=True, 0=False
    products_used = Column(Text, nullable=True)  # IDs de productos usados (JSON)
    
    # Favoritos
    is_favorite = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="recipes")

    def __repr__(self):
        return f"<Recipe(id={self.id}, title={self.title})>"
