"""
Modelo Product - Tabla de Productos del Inventario
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class ProductCategory(str, enum.Enum):
    """Categorías de productos"""
    FRUITS = "fruits"
    VEGETABLES = "vegetables"
    DAIRY = "dairy"
    MEAT = "meat"
    FISH = "fish"
    GRAINS = "grains"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    CONDIMENTS = "condiments"
    FROZEN = "frozen"
    BAKERY = "bakery"
    OTHER = "other"


class ProductLocation(str, enum.Enum):
    """Ubicación del producto"""
    FRIDGE = "fridge"
    FREEZER = "freezer"
    PANTRY = "pantry"


class ProductStatus(str, enum.Enum):
    """Estado del producto"""
    ACTIVE = "active"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    WASTED = "wasted"


class Product(Base):
    """
    Modelo de Producto
    Tabla: products
    """
    __tablename__ = "products"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información del producto
    name = Column(String, nullable=False, index=True)
    category = Column(Enum(ProductCategory), nullable=False)
    store = Column(String, nullable=True)  # 👈 NUEVA LÍNEA - Tienda donde se compró

    
    
    # Fechas
    purchase_date = Column(DateTime, default=datetime.utcnow)
    expiration_date = Column(DateTime, nullable=False, index=True)
    
    # Cantidad
    # Cantidad
    quantity = Column(Float, nullable=False)
    unit = Column(String, default="units")  # kg, g, liters, ml, units

    # Precio y estado de apertura (NUEVOS CAMPOS)
    price = Column(Float, nullable=True)  # Precio del producto
    is_opened = Column(Integer, default=0)  # 0=cerrado, 1=abierto
    opened_date = Column(DateTime, nullable=True)  # Fecha cuando se abrió
    
    # Ubicación y estado
    location = Column(Enum(ProductLocation), default=ProductLocation.PANTRY)
    status = Column(Enum(ProductStatus), default=ProductStatus.ACTIVE, index=True)
    
    # Extras
    image_url = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, expires={self.expiration_date})>"
    
    @property
    def days_until_expiration(self):
        """Calcula los días hasta la fecha de caducidad"""
        delta = self.expiration_date - datetime.utcnow()
        return delta.days
    
    @property
    def is_expired(self):
        """Verifica si el producto está caducado"""
        return datetime.utcnow() > self.expiration_date
    
    @property
    def is_expiring_soon(self, days=3):
        """Verifica si el producto caduca pronto"""
        return 0 <= self.days_until_expiration <= days
