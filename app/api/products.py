"""
API Endpoints de Productos
Aquí defines las rutas para crear, leer, actualizar y eliminar productos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.product import Product, ProductStatus
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductList

# Crear el router (como un "mini app" de FastAPI)
router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)


def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo producto en el inventario
    """
    user_id = 1
    
    # Crear el producto
    db_product = Product(
        user_id=user_id,
        name=product.name,
        category=product.category,
        store=product.store,
        purchase_date=product.purchase_date,
        expiration_date=product.expiration_date,
        quantity=product.quantity,
        unit=product.unit,
        price=product.price,  # NUEVO
        is_opened=1 if product.is_opened else 0,  # NUEVO
        opened_date=product.opened_date,  # NUEVO
        location=product.location,
        notes=product.notes,
        status=ProductStatus.ACTIVE
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product

@router.get("/", response_model=List[ProductList])
def list_products(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = "active",
    db: Session = Depends(get_db)
):
    """
    Listar todos los productos
    
    - skip: Número de productos a saltar (paginación)
    - limit: Número máximo de productos a devolver
    - status_filter: Filtrar por estado (active, consumed, expired, all)
    """
    # Por ahora user_id = 1
    user_id = 1
    
    query = db.query(Product).filter(Product.user_id == user_id)
    
    # Filtrar por estado
    if status_filter != "all":
        query = query.filter(Product.status == status_filter)
    
    # Ordenar por fecha de caducidad (los que caducan antes primero)
    query = query.order_by(Product.expiration_date)
    
    products = query.offset(skip).limit(limit).all()
    
    # Calcular días hasta caducidad para cada producto
    result = []
    for product in products:
        product_dict = ProductList.model_validate(product)
        product_dict.days_until_expiration = product.days_until_expiration
        result.append(product_dict)
    
    return result


@router.get("/expiring-soon", response_model=List[ProductList])
def get_expiring_soon(
    days: int = 3,
    db: Session = Depends(get_db)
):
    """
    Obtener productos que caducan pronto
    
    - days: Número de días (por defecto 3)
    
    Devuelve productos que caducan en los próximos X días
    """
    user_id = 1
    cutoff_date = datetime.utcnow() + timedelta(days=days)
    
    products = db.query(Product).filter(
        Product.user_id == user_id,
        Product.status == ProductStatus.ACTIVE,
        Product.expiration_date <= cutoff_date,
        Product.expiration_date >= datetime.utcnow()
    ).order_by(Product.expiration_date).all()
    
    result = []
    for product in products:
        product_dict = ProductList.model_validate(product)
        product_dict.days_until_expiration = product.days_until_expiration
        result.append(product_dict)
    
    return result


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un producto específico por ID
    """
    user_id = 1
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado"
        )
    
    # Calcular propiedades

    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un producto existente
    
    Solo envía los campos que quieras cambiar
    Ejemplo: {"quantity": 200, "notes": "Quedan 200g"}
    """
    user_id = 1
    
    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user_id
    ).first()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado"
        )
    
    # Actualizar solo los campos que se enviaron
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db_product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_product)
    
    
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar un producto del inventario
    """
    user_id = 1
    
    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user_id
    ).first()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado"
        )
    
    db.delete(db_product)
    db.commit()
    
    return None


@router.post("/{product_id}/mark-consumed", response_model=ProductResponse)
def mark_as_consumed(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Marcar un producto como consumido
    """
    user_id = 1
    
    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user_id
    ).first()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado"
        )
    
    db_product.status = ProductStatus.CONSUMED
    db_product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_product)
    
    return db_product