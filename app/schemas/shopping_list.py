"""
INSTRUCCIONES: Crea nuevo archivo app/schemas/shopping_list.py
Schemas de ShoppingList - Validación de lista de compra
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# ============================================
# SCHEMA PARA CREAR ITEM DE LISTA
# ============================================

class ShoppingListItemCreate(BaseModel):
    """
    Crear un item manual de lista de compra
    
    Ejemplo:
    {
        "ingredient_name": "Bacon",
        "category": "meat",
        "quantity_needed": 200,
        "unit": "g",
        "estimated_price": 3.50
    }
    """
    ingredient_name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., description="meat, vegetables, dairy, etc")
    quantity_needed: float = Field(..., gt=0)
    unit: str = Field(..., description="g, kg, ml, L, units, etc")
    estimated_price: Optional[float] = Field(None, ge=0)
    store: Optional[str] = None
    notes: Optional[str] = None
    weekly_menu_id: Optional[int] = None  # Si vino de un menú
    
    class Config:
        json_schema_extra = {
            "example": {
                "ingredient_name": "Bacon",
                "category": "meat",
                "quantity_needed": 200,
                "unit": "g",
                "estimated_price": 3.50,
                "store": "Mercadona"
            }
        }


# ============================================
# SCHEMA PARA ACTUALIZAR ITEM
# ============================================

class ShoppingListItemUpdate(BaseModel):
    """Actualizar un item de la lista"""
    is_bought: Optional[bool] = None
    actual_price: Optional[float] = Field(None, ge=0)
    store: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_bought": True,
                "actual_price": 3.20
            }
        }


# ============================================
# SCHEMA PARA RESPUESTA
# ============================================

class ShoppingListItemResponse(BaseModel):
    """Lo que devuelve la API"""
    id: int
    user_id: int
    ingredient_name: str
    category: str
    quantity_needed: float
    unit: str
    is_bought: bool
    estimated_price: Optional[float]
    actual_price: Optional[float]
    store: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMA PARA LISTA POR CATEGORÍA
# ============================================

class ShoppingListByCategory(BaseModel):
    """
    Lista de compra agrupada por categoría
    
    Ejemplo:
    {
        "meat": [
            {"name": "Bacon", "qty": 200, "unit": "g", "bought": false},
            {"name": "Pollo", "qty": 1, "unit": "kg", "bought": true}
        ],
        "vegetables": [
            {"name": "Tomate", "qty": 1.5, "unit": "kg", "bought": false}
        ]
    }
    """
    categories: dict  # {categoria: [items]}
    total_items: int
    total_bought: int
    total_pending: int
    estimated_total_cost: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "categories": {
                    "meat": [
                        {
                            "id": 1,
                            "name": "Bacon",
                            "quantity": 200,
                            "unit": "g",
                            "is_bought": False,
                            "estimated_price": 3.50,
                            "actual_price": None
                        }
                    ],
                    "vegetables": [
                        {
                            "id": 2,
                            "name": "Tomate",
                            "quantity": 1.5,
                            "unit": "kg",
                            "is_bought": False,
                            "estimated_price": 2.50,
                            "actual_price": None
                        }
                    ]
                },
                "total_items": 2,
                "total_bought": 0,
                "total_pending": 2,
                "estimated_total_cost": 6.00
            }
        }


# ============================================
# SCHEMA PARA RESUMEN DE LISTA
# ============================================

class ShoppingListSummary(BaseModel):
    """Resumen estadístico de la lista"""
    total_items: int
    bought_items: int
    pending_items: int
    completion_percentage: float  # 0-100%
    estimated_total_cost: float
    actual_total_cost: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_items": 15,
                "bought_items": 5,
                "pending_items": 10,
                "completion_percentage": 33.33,
                "estimated_total_cost": 45.50,
                "actual_total_cost": 42.30
            }
        }