"""
Schemas de Analytics - Validación de datos de analytics
VERSIÓN CORREGIDA - Compatible con analytics_service.py
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class OverviewStats(BaseModel):
    """Estadísticas generales del inventario"""
    total_products: int
    total_value: float
    expiring_soon: int
    expired: int
    consumed_last_30d: int
    wasted_last_30d: int
    waste_rate: float


# ✅ NUEVO: ProductSummary para index.html
class ProductSummary(BaseModel):
    """Resumen de productos por estado"""
    active: int
    expiring_soon_7days: int
    expired: int
    consumed: int
    wasted: int
    total: int


# ✅ NUEVO: FinancialSummary para index.html
class FinancialSummary(BaseModel):
    """Resumen financiero"""
    total_spent: float
    money_wasted: float
    current_inventory_value: float
    waste_rate_percentage: float
    avg_daily_spending: float


class CategoryDistribution(BaseModel):
    """Distribución por categoría"""
    category: str
    count: int
    total_value: float


class LocationDistribution(BaseModel):
    """Distribución por ubicación"""
    location: str
    count: int


class StoreDistribution(BaseModel):
    """Distribución por tienda"""
    store: str
    count: int
    product_count: int  # ✅ AGREGADO: para dashboard.html
    total_spent: float


class DailyTrend(BaseModel):
    """Tendencia diaria"""
    date: str
    added: int
    consumed: int


class ExpiringProduct(BaseModel):
    """Producto próximo a caducar"""
    id: int
    name: str
    category: str
    expiration_date: str
    days_until_expiration: int
    quantity: float
    unit: str
    location: str


class WasteMetrics(BaseModel):
    """Métricas de desperdicio"""
    total_wasted: int
    total_value_wasted: float
    total_products: int  # ✅ AGREGADO: total de productos en el periodo
    top_wasted_categories: List[Dict[str, Any]]
    waste_percentage: float


class PriceAnalysis(BaseModel):
    """Análisis de precios"""
    average_price: float
    total_inventory_value: float
    most_expensive_category: Optional[Dict[str, Any]]
    price_per_category: List[Dict[str, Any]]


# ✅ CORREGIDO: DashboardResponse con product_summary y financial_summary
class DashboardResponse(BaseModel):
    """Respuesta completa del dashboard"""
    overview: OverviewStats
    product_summary: ProductSummary  # ✅ NUEVO: Para index.html
    financial_summary: FinancialSummary  # ✅ NUEVO: Para index.html
    category_distribution: List[CategoryDistribution]
    location_distribution: List[LocationDistribution]
    store_distribution: List[StoreDistribution]
    daily_trends: List[DailyTrend]
    expiring_products: List[ExpiringProduct]
    waste_metrics: WasteMetrics
    price_analysis: PriceAnalysis
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "overview": {
                    "total_products": 25,
                    "total_value": 150.50,
                    "expiring_soon": 5,
                    "expired": 2,
                    "consumed_last_30d": 18,
                    "wasted_last_30d": 3,
                    "waste_rate": 14.29
                },
                "product_summary": {
                    "active": 25,
                    "expiring_soon_7days": 5,
                    "expired": 2,
                    "consumed": 18,
                    "wasted": 3,
                    "total": 48
                },
                "financial_summary": {
                    "total_spent": 245.80,
                    "money_wasted": 28.50,
                    "current_inventory_value": 150.50,
                    "waste_rate_percentage": 11.6,
                    "avg_daily_spending": 8.19
                },
                "category_distribution": [
                    {"category": "fruits", "count": 8, "total_value": 25.50}
                ],
                "location_distribution": [
                    {"location": "Nevera", "count": 12}
                ],
                "store_distribution": [
                    {"store": "Mercadona", "count": 15, "product_count": 15, "total_spent": 85.50}
                ],
                "daily_trends": [
                    {"date": "2025-01-15", "added": 5, "consumed": 3}
                ],
                "expiring_products": [],
                "waste_metrics": {
                    "total_wasted": 3,
                    "total_value_wasted": 12.50,
                    "total_products": 21,
                    "top_wasted_categories": [],
                    "waste_percentage": 14.29
                },
                "price_analysis": {
                    "average_price": 6.02,
                    "total_inventory_value": 150.50,
                    "most_expensive_category": None,
                    "price_per_category": [
                        {
                            "category": "fruits",
                            "average_price": 3.19,
                            "total_value": 25.50,
                            "product_count": 8
                        }
                    ]
                }
            }
        }


class CategoryInsight(BaseModel):
    """Insight de categoría"""
    category: str
    total_products: int
    expiring_soon: int
    expiring_percentage: float


class CategoryInsightsResponse(BaseModel):
    """Respuesta de insights por categoría"""
    category_insights: List[CategoryInsight]