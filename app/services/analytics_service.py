"""
Analytics Service - Lógica de negocio para análisis de datos del inventario
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.product import Product, ProductStatus, ProductCategory, ProductLocation
from app.models.user import User


class AnalyticsService:
    """Servicio para análisis y estadísticas del inventario"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self, user_id: int, days_back: int = 30) -> Dict:
        """
        Obtener estadísticas principales del dashboard
        """
        # Fecha de corte para el análisis
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # 1. ESTADÍSTICAS GENERALES
        total_products = self.db.query(Product).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.ACTIVE
        ).count()
        
        total_value = self.db.query(func.sum(Product.price * Product.quantity)).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.ACTIVE,
            Product.price.isnot(None)
        ).scalar() or 0.0
        
        # Productos que caducan en los próximos 7 días
        expiring_soon = self.db.query(Product).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.ACTIVE,
            Product.expiration_date <= datetime.utcnow() + timedelta(days=7),
            Product.expiration_date >= datetime.utcnow()
        ).count()
        
        # Productos caducados
        expired = self.db.query(Product).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.ACTIVE,
            Product.expiration_date < datetime.utcnow()
        ).count()
        
        # Productos consumidos en el periodo
        consumed = self.db.query(Product).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.CONSUMED,
            Product.updated_at >= cutoff_date
        ).count()
        
        # Productos desperdiciados en el periodo
        wasted = self.db.query(Product).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.WASTED,
            Product.updated_at >= cutoff_date
        ).count()
        
        # 2. DISTRIBUCIÓN POR CATEGORÍAS
        category_distribution = self._get_category_distribution(user_id)
        
        # 3. DISTRIBUCIÓN POR UBICACIONES
        location_distribution = self._get_location_distribution(user_id)
        
        # 4. PRODUCTOS POR TIENDA
        store_distribution = self._get_store_distribution(user_id)
        
        # 5. TENDENCIAS TEMPORALES (últimos 30 días)
        daily_trends = self._get_daily_trends(user_id, days_back)
        
        # 6. TOP PRODUCTOS PRÓXIMOS A CADUCAR
        expiring_products = self._get_expiring_products(user_id, 7)
        
        # 7. MÉTRICAS DE DESPERDICIO
        waste_metrics = self._get_waste_metrics(user_id, days_back)
        
        # 8. ANÁLISIS DE PRECIOS
        price_analysis = self._get_price_analysis(user_id)
        
        return {
            "overview": {
                "total_products": total_products,
                "total_value": round(total_value, 2),
                "expiring_soon": expiring_soon,
                "expired": expired,
                "consumed_last_30d": consumed,
                "wasted_last_30d": wasted,
                "waste_rate": round((wasted / (consumed + wasted) * 100) if (consumed + wasted) > 0 else 0, 2)
            },
            "category_distribution": category_distribution,
            "location_distribution": location_distribution,
            "store_distribution": store_distribution,
            "daily_trends": daily_trends,
            "expiring_products": expiring_products,
            "waste_metrics": waste_metrics,
            "price_analysis": price_analysis
        }
    
    def _get_category_distribution(self, user_id: int) -> List[Dict]:
        """Distribución de productos por categoría"""
        results = self.db.query(
            Product.category,
            func.count(Product.id).label('count'),
            func.sum(Product.price).label('total_value')
        ).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.ACTIVE
        ).group_by(Product.category).all()
        
        return [
            {
                "category": str(row.category.value),
                "count": row.count,
                "total_value": round(row.total_value or 0, 2)
            }
            for row in results
        ]
    
    def _get_location_distribution(self, user_id: int) -> List[Dict]:
        """Distribución de productos por ubicación"""
        results = self.db.query(
            Product.location,
            func.count(Product.id).label('count')
        ).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.ACTIVE
        ).group_by(Product.location).all()
        
        location_names = {
            'fridge': 'Nevera',
            'freezer': 'Congelador',
            'pantry': 'Despensa'
        }
        
        return [
            {
                "location": location_names.get(str(row.location.value), str(row.location.value)),
                "count": row.count
            }
            for row in results
        ]
    
    def _get_store_distribution(self, user_id: int) -> List[Dict]:
        """Distribución de productos por tienda"""
        results = self.db.query(
            Product.store,
            func.count(Product.id).label('count'),
            func.sum(Product.price).label('total_spent')
        ).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.ACTIVE,
            Product.store.isnot(None)
        ).group_by(Product.store).order_by(func.count(Product.id).desc()).limit(10).all()
        
        return [
            {
                "store": row.store,
                "count": row.count,
                "total_spent": round(row.total_spent or 0, 2)
            }
            for row in results
        ]
    
    def _get_daily_trends(self, user_id: int, days_back: int) -> List[Dict]:
        """Tendencias diarias de productos agregados/consumidos"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Productos agregados por día
        added = self.db.query(
            func.date(Product.created_at).label('date'),
            func.count(Product.id).label('count')
        ).filter(
            Product.user_id == user_id,
            Product.created_at >= cutoff_date
        ).group_by(func.date(Product.created_at)).all()
        
        # Productos consumidos por día
        consumed = self.db.query(
            func.date(Product.updated_at).label('date'),
            func.count(Product.id).label('count')
        ).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.CONSUMED,
            Product.updated_at >= cutoff_date
        ).group_by(func.date(Product.updated_at)).all()
        
        # Combinar resultados
        trends = {}
        for row in added:
            date_str = row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date)
            trends[date_str] = {"date": date_str, "added": row.count, "consumed": 0}
        
        for row in consumed:
            date_str = row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date)
            if date_str in trends:
                trends[date_str]["consumed"] = row.count
            else:
                trends[date_str] = {"date": date_str, "added": 0, "consumed": row.count}
        
        return sorted(trends.values(), key=lambda x: x['date'])
    
    def _get_expiring_products(self, user_id: int, days: int) -> List[Dict]:
        """Top productos próximos a caducar"""
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        
        products = self.db.query(Product).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.ACTIVE,
            Product.expiration_date <= cutoff_date,
            Product.expiration_date >= datetime.utcnow()
        ).order_by(Product.expiration_date).limit(10).all()
        
        return [
            {
                "id": p.id,
                "name": p.name,
                "category": str(p.category.value),
                "expiration_date": p.expiration_date.isoformat(),
                "days_until_expiration": p.days_until_expiration,
                "quantity": p.quantity,
                "unit": p.unit,
                "location": str(p.location.value)
            }
            for p in products
        ]
    
    def _get_waste_metrics(self, user_id: int, days_back: int) -> Dict:
        """Métricas de desperdicio"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Total desperdiciado
        wasted_products = self.db.query(Product).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.WASTED,
            Product.updated_at >= cutoff_date
        ).all()
        
        total_wasted = len(wasted_products)
        total_value_wasted = sum(p.price or 0 for p in wasted_products)
        
        # Categorías más desperdiciadas
        wasted_by_category = {}
        for p in wasted_products:
            cat = str(p.category.value)
            wasted_by_category[cat] = wasted_by_category.get(cat, 0) + 1
        
        top_wasted_categories = sorted(
            [{"category": k, "count": v} for k, v in wasted_by_category.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:5]
        
        return {
            "total_wasted": total_wasted,
            "total_value_wasted": round(total_value_wasted, 2),
            "top_wasted_categories": top_wasted_categories,
            "waste_percentage": round((total_wasted / (total_wasted + self.db.query(Product).filter(
                Product.user_id == user_id,
                Product.status == ProductStatus.CONSUMED,
                Product.updated_at >= cutoff_date
            ).count() or 1) * 100), 2)
        }
    
    def _get_price_analysis(self, user_id: int) -> Dict:
        """Análisis de precios"""
        products_with_price = self.db.query(Product).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.ACTIVE,
            Product.price.isnot(None)
        ).all()
        
        if not products_with_price:
            return {
                "average_price": 0,
                "total_inventory_value": 0,
                "most_expensive_category": None,
                "price_per_category": []
            }
        
        # Precio promedio
        avg_price = sum(p.price for p in products_with_price) / len(products_with_price)
        
        # Valor total del inventario
        total_value = sum(p.price * p.quantity for p in products_with_price)
        
        # Precio por categoría
        price_by_category = {}
        count_by_category = {}
        
        for p in products_with_price:
            cat = str(p.category.value)
            price_by_category[cat] = price_by_category.get(cat, 0) + p.price
            count_by_category[cat] = count_by_category.get(cat, 0) + 1
        
        price_per_category = [
            {
                "category": cat,
                "average_price": round(price_by_category[cat] / count_by_category[cat], 2),
                "total_value": round(price_by_category[cat], 2)
            }
            for cat in price_by_category
        ]
        
        # Categoría más cara
        most_expensive = max(price_per_category, key=lambda x: x['average_price']) if price_per_category else None
        
        return {
            "average_price": round(avg_price, 2),
            "total_inventory_value": round(total_value, 2),
            "most_expensive_category": most_expensive,
            "price_per_category": sorted(price_per_category, key=lambda x: x['total_value'], reverse=True)
        }
    
    def get_category_insights(self, user_id: int) -> Dict:
        """Insights detallados por categoría"""
        categories = self.db.query(Product.category, func.count(Product.id).label('count')).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.ACTIVE
        ).group_by(Product.category).all()
        
        insights = []
        for cat, count in categories:
            # Productos de esta categoría próximos a caducar
            expiring = self.db.query(Product).filter(
                Product.user_id == user_id,
                Product.category == cat,
                Product.status == ProductStatus.ACTIVE,
                Product.expiration_date <= datetime.utcnow() + timedelta(days=7)
            ).count()
            
            insights.append({
                "category": str(cat.value),
                "total_products": count,
                "expiring_soon": expiring,
                "expiring_percentage": round((expiring / count * 100) if count > 0 else 0, 2)
            })
        
        return {"category_insights": insights}