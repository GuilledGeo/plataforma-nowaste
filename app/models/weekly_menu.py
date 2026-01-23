"""
INSTRUCCIONES: Crea nuevo archivo app/models/weekly_menu.py
Modelo WeeklyMenu - Tabla para guardar menús semanales
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class WeeklyMenu(Base):
    """
    Modelo de Menú Semanal
    Tabla: weekly_menu
    
    Ejemplo de uso:
    ================
    - Usuario crea menú para semana 20-26 Enero
    - Lunes desayuno (breakfast): Tostadas con mermelada
    - Lunes comida (lunch): Pasta Carbonara (4 personas)
    - Lunes cena (dinner): Ensalada
    - Y así para todo la semana...
    
    El campo ingredients_needed guarda:
    {
        "total_servings": 4,
        "ingredients": [
            {
                "name": "Pasta",
                "quantity_needed": 400,
                "unit": "g",
                "inventory_available": 500,
                "status": "OK"
            },
            {
                "name": "Bacon",
                "quantity_needed": 200,
                "unit": "g",
                "inventory_available": 0,
                "status": "MISSING"
            }
        ]
    }
    """
    __tablename__ = "weekly_menu"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información de la semana
    # Ejemplo: 2025-01-20 (lunes de esa semana)
    week_start_date = Column(DateTime, nullable=False)
    
    # Información del día y comida específica
    day_of_week = Column(Integer, nullable=False)  # 0-6 (Lun-Dom) o 1-7
    meal_type = Column(String, nullable=False)  # "breakfast", "lunch", "dinner"
    
    # Receta seleccionada
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=True)
    
    # Número de personas/porciones para este menú
    # Ejemplo: Receta base es para 2, pero tú comes 4 personas = servings = 4
    servings = Column(Integer, default=2)
    
    # Guardamos los ingredientes CALCULADOS en el momento
    # Si el usuario edita receta después, esto no cambia
    # Formato: JSON con ingredientes × porciones × disponibilidad
    ingredients_needed = Column(JSON, nullable=True)
    
    # Estado
    is_completed = Column(Integer, default=0)
    notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="weekly_menus")
    recipe = relationship("Recipe")

    def __repr__(self):
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        day_name = days[self.day_of_week] if 0 <= self.day_of_week < 7 else "?"
        meal_names = {"breakfast": "🌅", "lunch": "🍽️", "dinner": "🌙"}
        meal_emoji = meal_names.get(self.meal_type, "?")
        return f"<WeeklyMenu({day_name} {meal_emoji}, {self.servings} personas)>"