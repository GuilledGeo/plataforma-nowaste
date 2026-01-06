"""
Recipe Service - Lógica de negocio para generar recetas con IA
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from anthropic import Anthropic

from app.models.product import Product, ProductStatus
from app.config import settings


class RecipeService:
    """Servicio para generar recomendaciones de recetas usando IA"""
    
    def __init__(self, db: Session):
        self.db = db
        # Inicializar cliente de Anthropic (Claude)
        self.client = None
        if settings.ANTHROPIC_API_KEY:
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def get_expiring_products(self, user_id: int, days: int = 7) -> List[Product]:
        """Obtener productos que caducan en los próximos N días"""
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        
        return self.db.query(Product).filter(
            Product.user_id == user_id,
            Product.status == ProductStatus.ACTIVE,
            Product.expiration_date <= cutoff_date,
            Product.expiration_date >= datetime.utcnow()
        ).order_by(Product.expiration_date).all()
    
    def generate_recipe_suggestions(
        self, 
        user_id: int, 
        days: int = 7, 
        max_recipes: int = 3,
        difficulty: Optional[str] = None
    ) -> dict:
        """Generar recomendaciones de recetas con productos próximos a caducar"""
        
        # Obtener productos que caducan pronto
        expiring_products = self.get_expiring_products(user_id, days)
        
        if not expiring_products:
            return {
                "expiring_products": [],
                "recipes_text": "No tienes productos próximos a caducar. ¡Tu inventario está bien gestionado! 🎉",
                "total_products": 0
            }
        
        # Si no hay API key configurada, devolver respuesta de ejemplo
        if not self.client:
            return {
                "expiring_products": [
                    {
                        "name": p.name,
                        "expiration_date": p.expiration_date.isoformat(),
                        "days_until_expiration": p.days_until_expiration,
                        "quantity": p.quantity,
                        "unit": p.unit
                    }
                    for p in expiring_products
                ],
                "recipes_text": "⚠️ API Key de Anthropic no configurada. Configura ANTHROPIC_API_KEY en el archivo .env para usar la generación de recetas con IA.\n\nMientras tanto, aquí están tus productos que caducan pronto para que busques recetas manualmente.",
                "total_products": len(expiring_products)
            }
        
        # Preparar lista de ingredientes para el prompt
        ingredients_list = []
        for p in expiring_products:
            days_left = p.days_until_expiration
            urgency = "¡MUY URGENTE!" if days_left <= 2 else "URGENTE" if days_left <= 5 else ""
            ingredients_list.append(
                f"- {p.name} ({p.quantity} {p.unit}, caduca en {days_left} días {urgency})"
            )
        
        ingredients_text = "\n".join(ingredients_list)
        
        # Construir el prompt para Claude
        difficulty_text = ""
        if difficulty:
            difficulty_map = {
                "easy": "fáciles y rápidas",
                "medium": "de dificultad media",
                "hard": "elaboradas y gourmet"
            }
            difficulty_text = f"Las recetas deben ser {difficulty_map.get(difficulty, 'variadas en dificultad')}."
        
        prompt = f"""Eres un chef experto y nutricionista. Tengo estos ingredientes en mi despensa que debo usar PRONTO porque están próximos a caducar:

{ingredients_text}

Por favor, recomiéndame {max_recipes} recetas deliciosas, saludables y fáciles de hacer. {difficulty_text}

Para CADA receta incluye:
1. **Nombre de la receta** (atractivo y apetecible)
2. **Ingredientes necesarios** (marca con ✅ los que YA TENGO de la lista, y lista los adicionales que necesitaría comprar)
3. **Tiempo de preparación** (minutos)
4. **Dificultad** (Fácil/Media/Difícil)
5. **Porciones** (cuántas personas)
6. **Instrucciones paso a paso** (numeradas y claras)
7. **Consejo del chef** (un tip para que salga perfecta)

PRIORIZA usar los ingredientes que caducan MÁS PRONTO. Si un ingrediente caduca en 1-2 días, ¡debe estar en la receta!

Formatea las recetas de manera clara y atractiva."""

        try:
            # Llamar a Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            recipes_text = message.content[0].text
            
        except Exception as e:
            recipes_text = f"⚠️ Error al generar recetas con IA: {str(e)}\n\nPor favor verifica tu API key de Anthropic."
        
        return {
            "expiring_products": [
                {
                    "name": p.name,
                    "expiration_date": p.expiration_date.isoformat(),
                    "days_until_expiration": p.days_until_expiration,
                    "quantity": p.quantity,
                    "unit": p.unit,
                    "store": p.store
                }
                for p in expiring_products
            ],
            "recipes_text": recipes_text,
            "total_products": len(expiring_products)
        }
    
    def generate_weekly_menu(self, user_id: int, include_all: bool = False) -> dict:
        """Generar menú semanal optimizado"""
        
        if include_all:
            # Todos los productos activos
            products = self.db.query(Product).filter(
                Product.user_id == user_id,
                Product.status == ProductStatus.ACTIVE
            ).order_by(Product.expiration_date).all()
        else:
            # Solo productos que caducan en los próximos 14 días
            products = self.get_expiring_products(user_id, days=14)
        
        if not products:
            return {
                "weekly_menu": "No hay productos suficientes en tu inventario para generar un menú semanal.",
                "total_products": 0,
                "expiring_soon": 0
            }
        
        if not self.client:
            return {
                "weekly_menu": "⚠️ API Key de Anthropic no configurada. Configura ANTHROPIC_API_KEY en el archivo .env para usar esta funcionalidad.",
                "total_products": len(products),
                "expiring_soon": len([p for p in products if p.days_until_expiration <= 3])
            }
        
        # Preparar inventario
        inventory_list = []
        for p in products:
            days_left = p.days_until_expiration
            priority = "🔴" if days_left <= 3 else "🟡" if days_left <= 7 else "🟢"
            inventory_list.append(
                f"{priority} {p.name} ({p.quantity} {p.unit}, caduca en {days_left} días)"
            )
        
        inventory_text = "\n".join(inventory_list)
        
        prompt = f"""Eres un nutricionista y chef profesional. Necesito que me crees un MENÚ SEMANAL (7 días) utilizando este inventario de alimentos:

{inventory_text}

Requisitos IMPORTANTES:
1. PRIORIZA usar productos marcados con 🔴 (caducan en 1-3 días)
2. Luego usa los marcados con 🟡 (caducan en 4-7 días)
3. Crea menús balanceados y variados
4. Incluye: Desayuno, Comida (almuerzo) y Cena para cada día
5. Indica qué productos del inventario se usan cada día
6. Las recetas deben ser realistas y fáciles de preparar

Formato para CADA DÍA:

**DÍA [número] - [nombre del día]**

🌅 **DESAYUNO**
- [Nombre del plato]
- Ingredientes del inventario usados: [lista]

🍽️ **COMIDA**
- [Nombre del plato]
- Ingredientes del inventario usados: [lista]

🌙 **CENA**
- [Nombre del plato]
- Ingredientes del inventario usados: [lista]

---

Sé creativo pero práctico. ¡Ayúdame a no desperdiciar comida!"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            menu_text = message.content[0].text
            
        except Exception as e:
            menu_text = f"⚠️ Error al generar menú con IA: {str(e)}"
        
        expiring_soon_count = len([p for p in products if p.days_until_expiration <= 3])
        
        return {
            "weekly_menu": menu_text,
            "total_products": len(products),
            "expiring_soon": expiring_soon_count
        }