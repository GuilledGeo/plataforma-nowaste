"""
Importar todos los modelos para que SQLAlchemy los reconozca
"""
from app.models.user import User
from app.models.product import Product, ProductCategory, ProductLocation, ProductStatus
from app.models.recipe import Recipe
from app.models.notification import Notification, NotificationType

__all__ = [
    "User",
    "Product",
    "ProductCategory",
    "ProductLocation",
    "ProductStatus",
    "Recipe",
    "Notification",
    "NotificationType",
]
