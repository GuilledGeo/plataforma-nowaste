"""
API Endpoints de Analytics - Dashboard y Estadísticas
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.analytics import DashboardResponse, CategoryInsightsResponse
from app.services.analytics_service import AnalyticsService
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    days_back: int = Query(default=30, ge=1, le=365, description="Días hacia atrás para el análisis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📊 Obtener estadísticas completas del dashboard
    
    Devuelve análisis completo del inventario incluyendo:
    - Estadísticas generales (productos, valor, caducidad)
    - Distribución por categorías y ubicaciones
    - Tendencias temporales
    - Productos próximos a caducar
    - Métricas de desperdicio
    - Análisis de precios
    
    **Parámetros:**
    - `days_back`: Número de días hacia atrás para el análisis (default: 30)
    
    **Requiere autenticación** - Solo muestra datos del usuario autenticado
    """
    service = AnalyticsService(db)
    result = service.get_dashboard_stats(
        user_id=current_user.id,
        days_back=days_back
    )
    
    return result


@router.get("/categories", response_model=CategoryInsightsResponse)
def get_category_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📈 Obtener insights detallados por categoría
    
    Devuelve análisis de cada categoría de productos incluyendo:
    - Total de productos por categoría
    - Productos próximos a caducar por categoría
    - Porcentaje de productos que caducan pronto
    
    **Requiere autenticación** - Solo muestra datos del usuario autenticado
    """
    service = AnalyticsService(db)
    result = service.get_category_insights(user_id=current_user.id)
    
    return result