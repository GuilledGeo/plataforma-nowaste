"""
INSTRUCCIONES: Reemplaza el contenido de tu app/models/recipe.py con esto
Modelo Recipe - Tabla de Recetas (ACTUALIZADO)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Recipe(Base):
    """
    Modelo de Receta (MEJORADO)
    Tabla: recipes
    
    IMPORTANTE: El campo 'ingredients' ahora es JSON estructurado:
    [
        {
            "name": "Pasta",
            "quantity": 200,
            "unit": "g",
            "category": "grains"
        },
        {
            "name": "Bacon",
            "quantity": 100,
            "unit": "g",
            "category": "meat"
        }
    ]
    """
    __tablename__ = "recipes"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información de la receta
    title = Column(String, nullable=False)
    
    # ⭐ CAMBIO IMPORTANTE: Ahora es JSON (no Text)
    ingredients = Column(JSON, nullable=False, default=[])  # Lista de ingredientes estructurados
    
    instructions = Column(Text, nullable=False)
    
    # Metadatos
    prep_time = Column(Integer, nullable=True)  # Minutos
    difficulty = Column(String, default="medium")  # easy, medium, hard
    
    # ⭐ IMPORTANTE: Porciones base (para cálculos)
    base_servings = Column(Integer, default=2)  # Esta receta es para X personas
    
    # Categoría de receta
    meal_type = Column(String, nullable=True)  # "breakfast", "lunch", "dinner"
    
    # AI Generated
    is_ai_generated = Column(Integer, default=1)  # Boolean: 1=True, 0=False
    
    # Favoritos
    is_favorite = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="recipes")

    def __repr__(self):
        return f"<Recipe(id={self.id}, title={self.title}, base_servings={self.base_servings})>"