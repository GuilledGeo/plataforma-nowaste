"""
Schemas de Product - Validación de datos
Similar a serializers en Django REST Framework
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.product import ProductCategory, ProductLocation, ProductStatus


# Schema para CREAR un producto (lo que el usuario envía)
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Nombre del producto")
    category: ProductCategory = Field(..., description="Categoría del producto")
    store: Optional[str] = Field(None, max_length=100, description="Tienda donde se compró (ej: Mercadona)")
    
    expiration_date: datetime = Field(..., description="Fecha de caducidad")
    purchase_date: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Fecha de compra")
    
    quantity: float = Field(..., gt=0, description="Cantidad del producto")
    unit: str = Field(default="units", max_length=20, description="Unidad (kg, g, liters, ml, units)")
    
    # NUEVOS CAMPOS
    price: Optional[float] = Field(None, ge=0, description="Precio del producto en euros")
    is_opened: bool = Field(default=False, description="¿Está abierto?")
    opened_date: Optional[datetime] = Field(None, description="Fecha cuando se abrió")
    
    location: ProductLocation = Field(default=ProductLocation.PANTRY, description="Ubicación")
    notes: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Raviolis",
                "category": "grains",
                "store": "Mercadona",
                "expiration_date": "2025-01-15T00:00:00",
                "purchase_date": "2025-01-06T00:00:00",
                "quantity": 250,
                "unit": "g",
                "price": 2.50,
                "is_opened": False,
                "location": "pantry",
                "notes": "Pasta fresca"
            }
        }


# Schema para ACTUALIZAR un producto (campos opcionales)
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[ProductCategory] = None
    store: Optional[str] = Field(None, max_length=100)
    
    expiration_date: Optional[datetime] = None
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=20)
    
    location: Optional[ProductLocation] = None
    status: Optional[ProductStatus] = None
    notes: Optional[str] = Field(None, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 200,
                "notes": "Quedan 200g"
            }
        }


# Schema de RESPUESTA (lo que la API devuelve)
class ProductResponse(BaseModel):
    id: int
    user_id: int
    name: str
    category: ProductCategory
    store: Optional[str]
    
    purchase_date: datetime
    expiration_date: datetime
    
    quantity: float
    unit: str
    
    # NUEVOS CAMPOS
    price: Optional[float]
    is_opened: Optional[bool]
    opened_date: Optional[datetime]
    
    location: ProductLocation
    status: ProductStatus
    
    image_url: Optional[str]
    notes: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    
    # Propiedades calculadas
    days_until_expiration: Optional[int] = None
    is_expired: Optional[bool] = None
    
    class Config:
        from_attributes = True


# Schema para listar productos con información resumida
class ProductList(BaseModel):
    id: int
    name: str
    category: ProductCategory
    store: Optional[str]
    expiration_date: datetime
    quantity: float
    unit: str
    price: Optional[float]  # NUEVO
    is_opened: Optional[bool]  # NUEVO
    location: ProductLocation
    status: ProductStatus
    days_until_expiration: Optional[int] = None
    
    class Config:
        from_attributes = True