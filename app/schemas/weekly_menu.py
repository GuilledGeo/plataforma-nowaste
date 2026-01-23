"""
INSTRUCCIONES: Crea nuevo archivo app/schemas/weekly_menu.py
Schemas de WeeklyMenu - Validación de datos de entrada/salida
Los schemas son como "plantillas" que validan que los datos sean correctos
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ============================================
# ENUMS (Valores fijos permitidos)
# ============================================

class MealType(str, Enum):
    """Tipos de comidas"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"


class DayOfWeek(int, Enum):
    """Días de la semana"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


# ============================================
# SCHEMA PARA INGREDIENTE NECESARIO
# ============================================

class IngredientNeeded(BaseModel):
    """Un ingrediente específico con su disponibilidad"""
    name: str
    quantity_needed: float
    unit: str
    inventory_available: float = 0
    status: str  # "OK" o "MISSING"
    missing_quantity: float = 0  # Cuánto falta
    category: Optional[str] = None


# ============================================
# SCHEMA PARA CREAR/ACTUALIZAR MENÚ
# ============================================

class WeeklyMenuCreate(BaseModel):
    """
    Lo que el usuario ENVÍA cuando añade algo al menú
    
    Ejemplo:
    {
        "week_start_date": "2025-01-20T00:00:00",
        "day_of_week": 0,  # Lunes
        "meal_type": "lunch",
        "recipe_id": 5,
        "servings": 4
    }
    """
    week_start_date: datetime = Field(..., description="Fecha inicio semana (Lunes)")
    day_of_week: int = Field(..., ge=0, le=6, description="0=Lunes, 6=Domingo")
    meal_type: MealType = Field(..., description="breakfast, lunch o dinner")
    recipe_id: int = Field(..., description="ID de receta")
    servings: int = Field(default=2, ge=1, le=20, description="Número de personas")
    notes: Optional[str] = Field(None, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "week_start_date": "2025-01-20T00:00:00",
                "day_of_week": 0,
                "meal_type": "lunch",
                "recipe_id": 5,
                "servings": 4,
                "notes": "Para la abuela"
            }
        }


class WeeklyMenuUpdate(BaseModel):
    """Actualizar un menú existente"""
    recipe_id: Optional[int] = None
    servings: Optional[int] = Field(None, ge=1, le=20)
    notes: Optional[str] = None


# ============================================
# SCHEMA PARA RESPUESTA (lo que devuelve la API)
# ============================================

class WeeklyMenuResponse(BaseModel):
    """La API devuelve esto cuando pides un menú"""
    id: int
    user_id: int
    week_start_date: datetime
    day_of_week: int
    meal_type: str
    recipe_id: Optional[int]
    servings: int
    ingredients_needed: Optional[List[IngredientNeeded]] = None
    notes: Optional[str]
    is_completed: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WeeklyMenuWithRecipe(WeeklyMenuResponse):
    """Menú pero incluyendo detalles de la receta"""
    recipe: Optional[dict] = None  # Detalles de la receta


# ============================================
# SCHEMA PARA RESPUESTA DE DISPONIBILIDAD
# ============================================

class AvailabilityCheck(BaseModel):
    """
    Resultado cuando preguntas: "¿Tengo ingredientes para esta receta?"
    """
    recipe_id: int
    recipe_title: str
    servings_requested: int
    total_ingredients: int
    available_count: int  # Cuántos tengo
    missing_count: int  # Cuántos faltan
    
    # Lista detallada
    ingredients: List[IngredientNeeded]
    
    # Resumen
    can_make_recipe: bool  # ¿Puedo hacer esta receta con lo que tengo?
    missing_percentage: float  # 0-100% de ingredientes que faltan
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipe_id": 5,
                "recipe_title": "Pasta Carbonara",
                "servings_requested": 4,
                "total_ingredients": 4,
                "available_count": 2,
                "missing_count": 2,
                "can_make_recipe": False,
                "missing_percentage": 50.0,
                "ingredients": [
                    {
                        "name": "Pasta",
                        "quantity_needed": 400,
                        "unit": "g",
                        "inventory_available": 500,
                        "status": "OK",
                        "missing_quantity": 0
                    },
                    {
                        "name": "Bacon",
                        "quantity_needed": 200,
                        "unit": "g",
                        "inventory_available": 0,
                        "status": "MISSING",
                        "missing_quantity": 200
                    }
                ]
            }
        }


# ============================================
# SCHEMA PARA MENÚ SEMANAL COMPLETO
# ============================================

class WeeklyMenuFull(BaseModel):
    """Vista completa de menú semanal (7 días × 3 comidas)"""
    week_start_date: datetime
    
    # Estructura: {dia: {comida: {detalles}}}
    menus: dict  # Detalles por día/comida
    
    # Resumen de la semana
    total_recipes: int
    recipes_with_missing_ingredients: int
    estimated_shopping_items: int  # Cuánto hay que comprar


# ============================================
# SCHEMA PARA MENÚ POR DÍA
# ============================================

class DayMenu(BaseModel):
    """Menú de un solo día (las 3 comidas)"""
    day_of_week: int
    day_name: str
    meals: dict  # {meal_type: WeeklyMenuResponse}