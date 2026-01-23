"""
INSTRUCCIONES: Crea nuevo archivo app/api/shopping_list.py
API Endpoints para Lista de Compra
Se genera AUTOMÁTICAMENTE del menú semanal
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.shopping_list import ShoppingList
from app.models.weekly_menu import WeeklyMenu
from app.utils.auth import get_current_user
from app.schemas.shopping_list import (
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    ShoppingListItemResponse,
    ShoppingListByCategory,
    ShoppingListSummary
)
from app.services.menu_service import MenuService

router = APIRouter()


# ================================================================
# ENDPOINT 1: Generar lista de compra automática
# ================================================================

@router.post("/generate")
def generate_shopping_list(
    week_start_date: str = Query(..., description="Formato: 2025-01-20"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🚀 Generar lista de compra automática del menú
    
    Endpoint:
    POST /api/shopping-list/generate?week_start_date=2025-01-20
    
    Qué hace:
    1. Lee TODO el menú de la semana
    2. Para cada receta, calcula ingredientes × porciones
    3. Compara con tu inventario actual
    4. Genera lista solo con lo que FALTA
    5. Agrupa por categoría
    6. Suma cantidades si aparecen múltiples veces
    
    Respuesta:
    {
        "week_start_date": "2025-01-20",
        "total_items_to_buy": 5,
        "items_by_category": {
            "meat": [
                {
                    "ingredient": "Bacon",
                    "quantity": 200,
                    "unit": "g",
                    "from_menus": ["Lunes-comida", "Miércoles-cena"],
                    "estimated_price": 3.50
                }
            ],
            "vegetables": [...]
        },
        "estimated_total_cost": 45.50
    }
    """
    
    try:
        week_start = datetime.fromisoformat(week_start_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Usa: YYYY-MM-DD"
        )
    
    service = MenuService(db)
    
    # Generar lista
    result = service.generate_shopping_list_from_menu(current_user.id, week_start)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    # Guardar en BD
    saved_items = service.save_shopping_list_to_db(current_user.id, week_start)
    
    return result


# ================================================================
# ENDPOINT 2: Obtener lista de compra (por categoría)
# ================================================================

@router.get("/by-category", response_model=ShoppingListByCategory)
def get_shopping_list_by_category(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🛒 Obtener lista de compra agrupada por categoría
    
    Endpoint:
    GET /api/shopping-list/by-category
    
    Respuesta:
    {
        "categories": {
            "meat": [
                {
                    "id": 1,
                    "name": "Bacon",
                    "quantity": 200,
                    "unit": "g",
                    "is_bought": false,
                    "estimated_price": 3.50,
                    "actual_price": null
                }
            ],
            "vegetables": [...]
        },
        "total_items": 5,
        "total_bought": 1,
        "total_pending": 4,
        "estimated_total_cost": 45.50
    }
    """
    
    # Obtener todos los items de lista
    items = db.query(ShoppingList).filter(
        ShoppingList.user_id == current_user.id,
        ShoppingList.is_bought == False  # Solo no comprados
    ).all()
    
    # Agrupar por categoría
    categories = {}
    total_cost = 0.0
    
    for item in items:
        if item.category not in categories:
            categories[item.category] = []
        
        categories[item.category].append({
            "id": item.id,
            "name": item.ingredient_name,
            "quantity": item.quantity_needed,
            "unit": item.unit,
            "is_bought": item.is_bought,
            "estimated_price": item.estimated_price,
            "actual_price": item.actual_price,
            "store": item.store,
            "notes": item.notes
        })
        
        total_cost += item.estimated_price or 0.0
    
    # Contar comprados vs pendientes
    all_items = db.query(ShoppingList).filter(
        ShoppingList.user_id == current_user.id
    ).all()
    
    bought_count = len([i for i in all_items if i.is_bought])
    total_count = len(all_items)
    pending_count = total_count - bought_count
    
    return {
        "categories": categories,
        "total_items": total_count,
        "total_bought": bought_count,
        "total_pending": pending_count,
        "estimated_total_cost": round(total_cost, 2)
    }


# ================================================================
# ENDPOINT 3: Obtener resumen de lista
# ================================================================

@router.get("/summary", response_model=ShoppingListSummary)
def get_shopping_list_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📊 Obtener resumen rápido de la lista de compra
    
    Endpoint:
    GET /api/shopping-list/summary
    
    Respuesta:
    {
        "total_items": 5,
        "bought_items": 1,
        "pending_items": 4,
        "completion_percentage": 20.0,
        "estimated_total_cost": 45.50,
        "actual_total_cost": 12.50
    }
    """
    
    items = db.query(ShoppingList).filter(
        ShoppingList.user_id == current_user.id
    ).all()
    
    if not items:
        return {
            "total_items": 0,
            "bought_items": 0,
            "pending_items": 0,
            "completion_percentage": 0.0,
            "estimated_total_cost": 0.0,
            "actual_total_cost": 0.0
        }
    
    bought = [i for i in items if i.is_bought]
    total = len(items)
    bought_count = len(bought)
    pending_count = total - bought_count
    
    # Calcular costos
    estimated_total = sum(i.estimated_price or 0.0 for i in items)
    actual_total = sum(i.actual_price or 0.0 for i in bought)
    
    completion_pct = (bought_count / total * 100) if total > 0 else 0.0
    
    return {
        "total_items": total,
        "bought_items": bought_count,
        "pending_items": pending_count,
        "completion_percentage": round(completion_pct, 1),
        "estimated_total_cost": round(estimated_total, 2),
        "actual_total_cost": round(actual_total, 2)
    }


# ================================================================
# ENDPOINT 4: Marcar item como comprado
# ================================================================

@router.put("/{item_id}/buy", response_model=ShoppingListItemResponse)
def mark_as_bought(
    item_id: int,
    update_data: ShoppingListItemUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✅ Marcar item de lista como comprado
    
    Endpoint:
    PUT /api/shopping-list/1/buy
    
    Body (opcional):
    {
        "actual_price": 3.20,
        "store": "Mercadona"
    }
    """
    
    item = db.query(ShoppingList).filter(
        ShoppingList.id == item_id,
        ShoppingList.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado"
        )
    
    item.is_bought = True
    item.bought_at = datetime.utcnow()
    
    # Actualizar precio real si se proporciona
    if update_data:
        if update_data.actual_price is not None:
            item.actual_price = update_data.actual_price
        if update_data.store is not None:
            item.store = update_data.store
    
    db.commit()
    db.refresh(item)
    
    return item


# ================================================================
# ENDPOINT 5: Desmarcar como comprado
# ================================================================

@router.put("/{item_id}/unbuy")
def mark_as_not_bought(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ↩️ Desmarcar item como comprado (opción de deshacer)
    
    Endpoint:
    PUT /api/shopping-list/1/unbuy
    """
    
    item = db.query(ShoppingList).filter(
        ShoppingList.id == item_id,
        ShoppingList.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado"
        )
    
    item.is_bought = False
    item.bought_at = None
    
    db.commit()
    db.refresh(item)
    
    return item


# ================================================================
# ENDPOINT 6: Añadir item manual a lista
# ================================================================

@router.post("/", response_model=ShoppingListItemResponse, status_code=status.HTTP_201_CREATED)
def create_shopping_item(
    item_data: ShoppingListItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ➕ Añadir item manual a lista de compra
    
    Endpoint:
    POST /api/shopping-list/
    
    Body:
    {
        "ingredient_name": "Leche",
        "category": "dairy",
        "quantity_needed": 2,
        "unit": "L",
        "estimated_price": 2.50
    }
    """
    
    db_item = ShoppingList(
        user_id=current_user.id,
        ingredient_name=item_data.ingredient_name,
        category=item_data.category,
        quantity_needed=item_data.quantity_needed,
        unit=item_data.unit,
        estimated_price=item_data.estimated_price,
        store=item_data.store,
        notes=item_data.notes,
        weekly_menu_id=item_data.weekly_menu_id
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item


# ================================================================
# ENDPOINT 7: Eliminar item de lista
# ================================================================

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🗑️ Eliminar item de lista
    
    Endpoint:
    DELETE /api/shopping-list/1
    """
    
    item = db.query(ShoppingList).filter(
        ShoppingList.id == item_id,
        ShoppingList.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado"
        )
    
    db.delete(item)
    db.commit()
    
    return None


# ================================================================
# ENDPOINT 8: Limpiar lista completa
# ================================================================

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_shopping_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🧹 Limpiar TODA la lista de compra
    
    Endpoint:
    DELETE /api/shopping-list/
    """
    
    db.query(ShoppingList).filter(
        ShoppingList.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return None