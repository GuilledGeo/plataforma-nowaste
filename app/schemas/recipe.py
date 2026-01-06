"""
Schemas de Recipe - Validación de datos de recetas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# Schema para crear una receta manualmente
class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    ingredients: str = Field(..., description="Ingredientes en formato texto o JSON")
    instructions: str = Field(..., description="Instrucciones paso a paso")
    prep_time: Optional[int] = Field(None, description="Tiempo de preparación en minutos")
    difficulty: str = Field(default="medium", description="Dificultad: easy, medium, hard")
    servings: int = Field(default=2, description="Número de porciones")
    products_used: Optional[str] = Field(None, description="IDs de productos usados (JSON)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Pasta con tomate",
                "ingredients": "Pasta, tomate, ajo, aceite",
                "instructions": "1. Hervir pasta\n2. Hacer salsa\n3. Mezclar",
                "prep_time": 20,
                "difficulty": "easy",
                "servings": 2
            }
        }


# Schema de respuesta
class RecipeResponse(BaseModel):
    id: int
    user_id: int
    title: str
    ingredients: str
    instructions: str
    prep_time: Optional[int]
    difficulty: str
    servings: int
    is_ai_generated: bool
    products_used: Optional[str]
    is_favorite: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schema para la sugerencia de recetas por IA
class RecipeSuggestionRequest(BaseModel):
    days_until_expiration: int = Field(default=7, ge=1, le=30, description="Días a considerar para productos que caducan")
    max_recipes: int = Field(default=3, ge=1, le=5, description="Número máximo de recetas a generar")
    difficulty: Optional[str] = Field(None, description="Filtrar por dificultad: easy, medium, hard")
    
    class Config:
        json_schema_extra = {
            "example": {
                "days_until_expiration": 7,
                "max_recipes": 3,
                "difficulty": "easy"
            }
        }


# Schema para la respuesta de sugerencias
class RecipeSuggestionResponse(BaseModel):
    expiring_products: List[dict] = Field(..., description="Lista de productos próximos a caducar")
    recipes_text: str = Field(..., description="Recetas generadas por IA en formato texto")
    total_products: int = Field(..., description="Total de productos considerados")
    
    class Config:
        json_schema_extra = {
            "example": {
                "expiring_products": [
                    {"name": "Raviolis", "days_until_expiration": 9, "quantity": 250, "unit": "g"}
                ],
                "recipes_text": "RECETA 1: Raviolis con mantequilla...",
                "total_products": 1
            }
        }


# Schema para menú semanal
class WeeklyMenuRequest(BaseModel):
    include_all_products: bool = Field(default=False, description="Incluir todos los productos o solo los que caducan pronto")
    
    class Config:
        json_schema_extra = {
            "example": {
                "include_all_products": False
            }
        }


class WeeklyMenuResponse(BaseModel):
    weekly_menu: str = Field(..., description="Menú semanal generado por IA")
    total_products: int
    expiring_soon: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "weekly_menu": "DÍA 1:\n- Desayuno: ...\n- Comida: ...\n- Cena: ...",
                "total_products": 10,
                "expiring_soon": 3
            }
        }