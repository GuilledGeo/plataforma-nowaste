"""
INSTRUCCIONES: Crea nuevo archivo app/api/menu.py
API Endpoints para Menú Semanal
Estos son los BOTONES que presiona el frontend
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.weekly_menu import WeeklyMenu
from app.models.recipe import Recipe
from app.utils.auth import get_current_user
from app.schemas.weekly_menu import (
    WeeklyMenuCreate, 
    WeeklyMenuUpdate, 
    WeeklyMenuResponse,
    AvailabilityCheck
)
from app.services.menu_service import MenuService

router = APIRouter()


# ================================================================
# ENDPOINT 1: Crear menú (Añadir receta a un día/comida)
# ================================================================

@router.post("/", response_model=WeeklyMenuResponse, status_code=status.HTTP_201_CREATED)
def create_menu(
    menu_data: WeeklyMenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ➕ Añadir receta al menú semanal
    
    Endpoint:
    POST /api/menu/
    
    Body:
    {
        "week_start_date": "2025-01-20T00:00:00",
        "day_of_week": 0,
        "meal_type": "lunch",
        "recipe_id": 5,
        "servings": 4
    }
    
    Respuesta:
    {
        "id": 1,
        "week_start_date": "2025-01-20T00:00:00",
        "day_of_week": 0,
        "meal_type": "lunch",
        "recipe_id": 5,
        "servings": 4,
        "ingredients_needed": {...},
        ...
    }
    """
    
    # Validar que la receta existe
    recipe = db.query(Recipe).filter(
        Recipe.id == menu_data.recipe_id,
        Recipe.user_id == current_user.id
    ).first()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receta no encontrada"
        )
    
    # Verificar disponibilidad de ingredientes
    service = MenuService(db)
    availability = service.check_ingredient_availability(
        current_user.id,
        recipe,
        menu_data.servings
    )
    
    # Crear menú
    db_menu = WeeklyMenu(
        user_id=current_user.id,
        week_start_date=menu_data.week_start_date,
        day_of_week=menu_data.day_of_week,
        meal_type=menu_data.meal_type,
        recipe_id=menu_data.recipe_id,
        servings=menu_data.servings,
        ingredients_needed=availability["ingredients"],
        notes=menu_data.notes
    )
    
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    
    return db_menu


# ================================================================
# ENDPOINT 2: Obtener menú semanal completo
# ================================================================

@router.get("/week")
def get_weekly_menu(
    week_start_date: str = Query(..., description="Formato: 2025-01-20"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📅 Obtener menú semanal completo
    
    Endpoint:
    GET /api/menu/week?week_start_date=2025-01-20
    
    Devuelve:
    {
        "week_start_date": "2025-01-20",
        "days": {
            "0": {
                "day_name": "Lunes",
                "meals": {
                    "breakfast": {...},
                    "lunch": {...},
                    "dinner": {...}
                }
            },
            ...
        }
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
    result = service.get_weekly_menu(current_user.id, week_start)
    
    return result


# ================================================================
# ENDPOINT 3: Verificar disponibilidad de ingredientes
# ================================================================

@router.get("/check-availability/{recipe_id}", response_model=AvailabilityCheck)
def check_availability(
    recipe_id: int,
    servings: int = Query(default=2, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✅❌ Verificar disponibilidad de ingredientes para una receta
    
    Endpoint:
    GET /api/menu/check-availability/5?servings=4
    
    Qué hace:
    1. Obtiene receta ID 5
    2. Calcula ingredientes para 4 personas
    3. Compara con tu inventario
    4. Devuelve: ✅ TENGO o ❌ FALTA
    
    Respuesta:
    {
        "recipe_id": 5,
        "recipe_title": "Pasta Carbonara",
        "can_make_recipe": false,
        "total_ingredients": 4,
        "available_count": 2,
        "missing_count": 2,
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
    """
    
    # Obtener receta
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == current_user.id
    ).first()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receta no encontrada"
        )
    
    # Verificar disponibilidad
    service = MenuService(db)
    result = service.check_ingredient_availability(
        current_user.id,
        recipe,
        servings
    )
    
    return result


# ================================================================
# ENDPOINT 4: Actualizar menú
# ================================================================

@router.put("/{menu_id}", response_model=WeeklyMenuResponse)
def update_menu(
    menu_id: int,
    menu_update: WeeklyMenuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✏️ Actualizar menú existente
    
    Endpoint:
    PUT /api/menu/1
    
    Body:
    {
        "servings": 6,
        "notes": "Sin lactosa"
    }
    """
    
    # Obtener menú
    menu = db.query(WeeklyMenu).filter(
        WeeklyMenu.id == menu_id,
        WeeklyMenu.user_id == current_user.id
    ).first()
    
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menú no encontrado"
        )
    
    # Actualizar campos si se proporcionan
    if menu_update.recipe_id is not None:
        # Validar nueva receta
        recipe = db.query(Recipe).filter(
            Recipe.id == menu_update.recipe_id,
            Recipe.user_id == current_user.id
        ).first()
        
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nueva receta no encontrada"
            )
        
        menu.recipe_id = menu_update.recipe_id
    
    if menu_update.servings is not None:
        menu.servings = menu_update.servings
    
    if menu_update.notes is not None:
        menu.notes = menu_update.notes
    
    # Recalcular ingredientes disponibles si cambiaron
    if menu.recipe_id:
        service = MenuService(db)
        availability = service.check_ingredient_availability(
            current_user.id,
            menu.recipe,
            menu.servings
        )
        menu.ingredients_needed = availability["ingredients"]
    
    menu.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(menu)
    
    return menu


# ================================================================
# ENDPOINT 5: Eliminar menú
# ================================================================

@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🗑️ Eliminar entrada del menú
    
    Endpoint:
    DELETE /api/menu/1
    """
    
    menu = db.query(WeeklyMenu).filter(
        WeeklyMenu.id == menu_id,
        WeeklyMenu.user_id == current_user.id
    ).first()
    
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menú no encontrado"
        )
    
    db.delete(menu)
    db.commit()
    
    return None