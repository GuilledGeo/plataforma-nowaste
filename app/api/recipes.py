"""
API Endpoints de Recetas
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.recipe import (
    RecipeSuggestionRequest,
    RecipeSuggestionResponse,
    WeeklyMenuRequest,
    WeeklyMenuResponse,
    RecipeCreate,
    RecipeResponse
)
from app.services.recipe_service import RecipeService
from app.models.recipe import Recipe

router = APIRouter()


@router.post("/suggest", response_model=RecipeSuggestionResponse)
def suggest_recipes(
    request: RecipeSuggestionRequest,
    db: Session = Depends(get_db)
):
    """
    🤖 Generar sugerencias de recetas usando IA
    
    Analiza los productos que caducan pronto y sugiere recetas deliciosas.
    Usa Claude AI para generar recetas personalizadas.
    
    Ejemplo de uso:
    {
        "days_until_expiration": 7,
        "max_recipes": 3,
        "difficulty": "easy"
    }
    """
    # Por ahora user_id = 1 (sin autenticación)
    user_id = 1
    
    service = RecipeService(db)
    result = service.generate_recipe_suggestions(
        user_id=user_id,
        days=request.days_until_expiration,
        max_recipes=request.max_recipes,
        difficulty=request.difficulty
    )
    
    return result


@router.post("/weekly-menu", response_model=WeeklyMenuResponse)
def generate_weekly_menu(
    request: WeeklyMenuRequest,
    db: Session = Depends(get_db)
):
    """
    📅 Generar menú semanal optimizado
    
    Crea un plan de comidas para 7 días usando tus productos,
    priorizando los que caducan más pronto.
    """
    user_id = 1
    
    service = RecipeService(db)
    result = service.generate_weekly_menu(
        user_id=user_id,
        include_all=request.include_all_products
    )
    
    return result


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def save_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db)
):
    """
    💾 Guardar una receta manualmente
    
    Guarda una receta en tus favoritos para consultarla después.
    """
    user_id = 1
    
    db_recipe = Recipe(
        user_id=user_id,
        title=recipe.title,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        prep_time=recipe.prep_time,
        difficulty=recipe.difficulty,
        servings=recipe.servings,
        products_used=recipe.products_used,
        is_ai_generated=0  # Manual
    )
    
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    
    return db_recipe


@router.get("/", response_model=list[RecipeResponse])
def list_recipes(
    skip: int = 0,
    limit: int = 50,
    favorites_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    📋 Listar recetas guardadas
    """
    user_id = 1
    
    query = db.query(Recipe).filter(Recipe.user_id == user_id)
    
    if favorites_only:
        query = query.filter(Recipe.is_favorite == 1)
    
    recipes = query.order_by(Recipe.created_at.desc()).offset(skip).limit(limit).all()
    
    return recipes


@router.put("/{recipe_id}/favorite", response_model=RecipeResponse)
def toggle_favorite(
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """
    ⭐ Marcar/Desmarcar receta como favorita
    """
    user_id = 1
    
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == user_id
    ).first()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receta no encontrada"
        )
    
    # Toggle favorite
    recipe.is_favorite = 0 if recipe.is_favorite else 1
    db.commit()
    db.refresh(recipe)
    
    return recipe