"""
INSTRUCCIONES: Crea nuevo archivo app/services/menu_service.py
Menu Service - LÓGICA INTELIGENTE del sistema
Este es el CEREBRO que calcula ingredientes, disponibilidad, lista compra, etc
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.product import Product, ProductStatus
from app.models.weekly_menu import WeeklyMenu
from app.models.recipe import Recipe
from app.models.shopping_list import ShoppingList


class MenuService:
    """
    Servicio para gestionar menús semanales
    
    Funciones principales:
    - Calcular ingredientes para una receta × porciones
    - Comparar con inventario actual
    - Generar lista de compra automáticamente
    - Verificar disponibilidad de ingredientes
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ================================================================
    # FUNCIÓN 1: Calcular ingredientes × porciones
    # ================================================================
    
    def calculate_ingredients_for_servings(
        self, 
        recipe: Recipe, 
        requested_servings: int
    ) -> Dict:
        """
        Calcula ingredientes ajustados por número de personas
        
        Ejemplo:
        ========
        Receta base: Pasta Carbonara para 2 personas
        Ingredientes base:
        - Pasta: 200g
        - Bacon: 100g
        - Huevos: 2
        
        Usuario solicita: 4 personas
        
        Cálculo:
        - Multiplicador: 4 / 2 = 2
        - Pasta: 200 × 2 = 400g
        - Bacon: 100 × 2 = 200g
        - Huevos: 2 × 2 = 4
        
        DEVUELVE:
        {
            "recipe_id": 1,
            "recipe_title": "Pasta Carbonara",
            "base_servings": 2,
            "requested_servings": 4,
            "multiplier": 2.0,
            "ingredients": [
                {
                    "name": "Pasta",
                    "quantity_base": 200,
                    "quantity_calculated": 400,
                    "unit": "g",
                    "category": "grains"
                },
                ...
            ]
        }
        """
        
        # Validar
        if not recipe or not recipe.ingredients:
            return {
                "error": "Receta no válida o sin ingredientes",
                "recipe_id": recipe.id if recipe else None
            }
        
        # Calcular multiplicador
        multiplier = requested_servings / recipe.base_servings
        
        # Procesar ingredientes
        calculated_ingredients = []
        
        for ingredient in recipe.ingredients:
            calculated_qty = ingredient.get("quantity", 0) * multiplier
            
            calculated_ingredients.append({
                "name": ingredient.get("name"),
                "quantity_base": ingredient.get("quantity"),
                "quantity_calculated": round(calculated_qty, 2),
                "unit": ingredient.get("unit"),
                "category": ingredient.get("category"),
                "notes": ingredient.get("notes")
            })
        
        return {
            "recipe_id": recipe.id,
            "recipe_title": recipe.title,
            "base_servings": recipe.base_servings,
            "requested_servings": requested_servings,
            "multiplier": round(multiplier, 2),
            "ingredients": calculated_ingredients
        }
    
    # ================================================================
    # FUNCIÓN 2: Verificar disponibilidad en inventario
    # ================================================================
    
    def check_ingredient_availability(
        self,
        user_id: int,
        recipe: Recipe,
        requested_servings: int
    ) -> Dict:
        """
        Compara ingredientes calculados vs lo que tienes en inventario
        
        DEVUELVE:
        {
            "recipe_id": 1,
            "recipe_title": "Pasta Carbonara",
            "can_make_recipe": False,
            "total_ingredients": 4,
            "available_count": 2,  # Tengo
            "missing_count": 2,    # Falta
            "missing_percentage": 50.0,
            "ingredients": [
                {
                    "name": "Pasta",
                    "quantity_needed": 400,
                    "unit": "g",
                    "inventory_available": 500,
                    "status": "OK",  # o "MISSING"
                    "missing_quantity": 0,
                    "category": "grains"
                },
                {
                    "name": "Bacon",
                    "quantity_needed": 200,
                    "unit": "g",
                    "inventory_available": 0,
                    "status": "MISSING",
                    "missing_quantity": 200,
                    "category": "meat"
                }
            ]
        }
        """
        
        # Paso 1: Calcular ingredientes necesarios
        calculated = self.calculate_ingredients_for_servings(recipe, requested_servings)
        
        if "error" in calculated:
            return calculated
        
        # Paso 2: Verificar disponibilidad en inventario
        ingredients_data = []
        available_count = 0
        missing_count = 0
        
        for ingredient in calculated["ingredients"]:
            ingredient_name = ingredient["name"]
            quantity_needed = ingredient["quantity_calculated"]
            unit = ingredient["unit"]
            category = ingredient["category"]
            
            # Buscar en inventario
            product_in_inventory = self.db.query(Product).filter(
                and_(
                    Product.user_id == user_id,
                    Product.name.ilike(f"%{ingredient_name}%"),  # Búsqueda parcial
                    Product.status == ProductStatus.ACTIVE
                )
            ).first()
            
            if product_in_inventory and product_in_inventory.quantity >= quantity_needed:
                # ✅ TENGO SUFICIENTE
                status = "OK"
                available_count += 1
                missing_qty = 0
            else:
                # ❌ FALTA O NO TENGO
                status = "MISSING"
                missing_count += 1
                available_qty = product_in_inventory.quantity if product_in_inventory else 0
                missing_qty = quantity_needed - available_qty
            
            ingredients_data.append({
                "name": ingredient_name,
                "quantity_needed": quantity_needed,
                "unit": unit,
                "inventory_available": product_in_inventory.quantity if product_in_inventory else 0,
                "status": status,
                "missing_quantity": missing_qty,
                "category": category
            })
        
        # Paso 3: Calcular resumen
        total_ingredients = len(calculated["ingredients"])
        can_make = missing_count == 0
        missing_percentage = (missing_count / total_ingredients * 100) if total_ingredients > 0 else 0
        
        return {
            "recipe_id": recipe.id,
            "recipe_title": recipe.title,
            "servings_requested": requested_servings,
            "can_make_recipe": can_make,
            "total_ingredients": total_ingredients,
            "available_count": available_count,
            "missing_count": missing_count,
            "missing_percentage": round(missing_percentage, 1),
            "ingredients": ingredients_data
        }
    
    # ================================================================
    # FUNCIÓN 3: Generar lista de compra automática
    # ================================================================
    
    def generate_shopping_list_from_menu(
        self,
        user_id: int,
        week_start_date: datetime
    ) -> Dict:
        """
        Genera lista de compra AUTOMÁTICA del menú semanal
        
        Proceso:
        1. Obtiene TODOS los menús de esa semana
        2. Para cada menú, calcula ingredientes × porciones
        3. Compara con inventario
        4. AGREGA a ShoppingList solo lo que FALTA
        5. AGRUPA por categoría y suma cantidades
        
        DEVUELVE:
        {
            "week_start_date": "2025-01-20",
            "total_items_to_buy": 5,
            "items_by_category": {
                "meat": [
                    {
                        "ingredient": "Bacon",
                        "quantity": 200,
                        "unit": "g",
                        "from_menus": ["Lunes-lunch", "Miércoles-dinner"],
                        "estimated_price": 3.50
                    }
                ],
                "vegetables": [...]
            },
            "estimated_total_cost": 45.50
        }
        """
        
        # Paso 1: Obtener todos los menús de esa semana
        week_end = week_start_date + timedelta(days=7)
        
        menus = self.db.query(WeeklyMenu).filter(
            and_(
                WeeklyMenu.user_id == user_id,
                WeeklyMenu.week_start_date >= week_start_date,
                WeeklyMenu.week_start_date < week_end
            )
        ).all()
        
        if not menus:
            return {
                "error": "No hay menú para esta semana",
                "week_start_date": week_start_date.isoformat()
            }
        
        # Paso 2: Acumular ingredientes que FALTAN
        shopping_items = {}  # {ingredient_name: {qty, unit, category, from_menus}}
        
        for menu in menus:
            if not menu.recipe_id:
                continue
            
            recipe = menu.recipe
            
            # Verificar disponibilidad
            availability = self.check_ingredient_availability(
                user_id, 
                recipe, 
                menu.servings
            )
            
            # Procesar solo ingredientes FALTANTES
            for ingredient in availability.get("ingredients", []):
                if ingredient["status"] == "MISSING":
                    ing_name = ingredient["name"]
                    
                    # Obtener día y comida para referencia
                    days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sá", "Dom"]
                    meals = {"breakfast": "desayuno", "lunch": "comida", "dinner": "cena"}
                    day_label = days[menu.day_of_week] if 0 <= menu.day_of_week < 7 else "?"
                    meal_label = meals.get(menu.meal_type, "?")
                    menu_ref = f"{day_label}-{meal_label}"
                    
                    if ing_name in shopping_items:
                        # Ya existe, sumar cantidad
                        shopping_items[ing_name]["quantity"] += ingredient["missing_quantity"]
                        shopping_items[ing_name]["from_menus"].append(menu_ref)
                    else:
                        # Nuevo item
                        shopping_items[ing_name] = {
                            "quantity": ingredient["missing_quantity"],
                            "unit": ingredient["unit"],
                            "category": ingredient["category"],
                            "from_menus": [menu_ref]
                        }
        
        # Paso 3: Agrupar por categoría
        items_by_category = {}
        total_cost = 0.0
        
        for ing_name, ing_data in shopping_items.items():
            category = ing_data["category"]
            
            if category not in items_by_category:
                items_by_category[category] = []
            
            # Estimar precio (simple: asumimos €1.50 por 100g)
            estimated_price = round((ing_data["quantity"] / 100) * 1.50, 2)
            
            items_by_category[category].append({
                "ingredient": ing_name,
                "quantity": ing_data["quantity"],
                "unit": ing_data["unit"],
                "from_menus": ing_data["from_menus"],
                "estimated_price": estimated_price
            })
            
            total_cost += estimated_price
        
        return {
            "week_start_date": week_start_date.isoformat(),
            "total_items_to_buy": len(shopping_items),
            "items_by_category": items_by_category,
            "estimated_total_cost": round(total_cost, 2)
        }
    
    # ================================================================
    # FUNCIÓN 4: Guardar lista de compra en BD
    # ================================================================
    
    def save_shopping_list_to_db(
        self,
        user_id: int,
        week_start_date: datetime
    ) -> List[ShoppingList]:
        """
        Guarda la lista de compra generada en la base de datos
        """
        
        # Primero, limpiar lista antigua si existe
        self.db.query(ShoppingList).filter(
            ShoppingList.user_id == user_id
        ).delete()
        self.db.commit()
        
        # Generar nueva lista
        shopping_data = self.generate_shopping_list_from_menu(user_id, week_start_date)
        
        if "error" in shopping_data:
            return []
        
        # Crear registros en BD
        shopping_list_items = []
        
        for category, items in shopping_data.get("items_by_category", {}).items():
            for item in items:
                shopping_item = ShoppingList(
                    user_id=user_id,
                    ingredient_name=item["ingredient"],
                    category=category,
                    quantity_needed=item["quantity"],
                    unit=item["unit"],
                    estimated_price=item["estimated_price"],
                    is_bought=False
                )
                self.db.add(shopping_item)
                shopping_list_items.append(shopping_item)
        
        self.db.commit()
        
        return shopping_list_items
    
    # ================================================================
    # FUNCIÓN 5: Obtener menú semanal completo
    # ================================================================
    
    def get_weekly_menu(
        self,
        user_id: int,
        week_start_date: datetime
    ) -> Dict:
        """
        Obtiene el menú semanal completo formateado
        
        Estructura:
        {
            "week_start_date": "2025-01-20",
            "days": {
                "0": {  # Lunes
                    "day_name": "Lunes",
                    "breakfast": {...},
                    "lunch": {...},
                    "dinner": {...}
                },
                ...
            }
        }
        """
        
        # Obtener menús de la semana
        week_end = week_start_date + timedelta(days=7)
        menus = self.db.query(WeeklyMenu).filter(
            and_(
                WeeklyMenu.user_id == user_id,
                WeeklyMenu.week_start_date >= week_start_date,
                WeeklyMenu.week_start_date < week_end
            )
        ).all()
        
        # Organizar por día
        days_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meal_names = {"breakfast": "🌅 Desayuno", "lunch": "🍽️ Comida", "dinner": "🌙 Cena"}
        
        days_dict = {}
        for i in range(7):
            days_dict[str(i)] = {
                "day_name": days_names[i],
                "meals": {}
            }
        
        for menu in menus:
            day_key = str(menu.day_of_week)
            
            menu_data = {
                "id": menu.id,
                "recipe_id": menu.recipe_id,
                "recipe_title": menu.recipe.title if menu.recipe else "Sin seleccionar",
                "servings": menu.servings,
                "ingredients_needed": menu.ingredients_needed,
                "notes": menu.notes
            }
            
            days_dict[day_key]["meals"][menu.meal_type] = menu_data
        
        return {
            "week_start_date": week_start_date.isoformat(),
            "days": days_dict
        }