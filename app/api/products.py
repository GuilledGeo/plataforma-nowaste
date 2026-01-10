"""
API Endpoints de Productos - Protegido por usuario
Cada usuario solo ve y maneja sus propios productos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.product import Product, ProductStatus
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductList
from app.utils.auth import get_current_user

# Crear el router
router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear un nuevo producto en el inventario del usuario autenticado
    """
    # Crear el producto con el ID del usuario autenticado
    db_product = Product(
        user_id=current_user.id,  # Usar ID del usuario autenticado
        name=product.name,
        category=product.category,
        store=product.store,
        purchase_date=product.purchase_date,
        expiration_date=product.expiration_date,
        quantity=product.quantity,
        unit=product.unit,
        price=product.price,
        is_opened=1 if product.is_opened else 0,
        opened_date=product.opened_date,
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Listar productos del usuario autenticado
    """
    # Filtrar por usuario autenticado
    query = db.query(Product).filter(Product.user_id == current_user.id)
    
    # Filtrar por estado
    if status_filter != "all":
        query = query.filter(Product.status == status_filter)
    
    # Ordenar por fecha de caducidad
    query = query.order_by(Product.expiration_date)
    
    products = query.offset(skip).limit(limit).all()
    
    # Calcular días hasta caducidad
    result = []
    for product in products:
        product_dict = ProductList.model_validate(product)
        product_dict.days_until_expiration = product.days_until_expiration
        result.append(product_dict)
    
    return result


@router.get("/expiring-soon", response_model=List[ProductList])
def get_expiring_soon(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener productos del usuario que caducan pronto
    """
    cutoff_date = datetime.utcnow() + timedelta(days=days)
    
    products = db.query(Product).filter(
        Product.user_id == current_user.id,  # Solo del usuario autenticado
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener un producto específico (solo si pertenece al usuario)
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id  # Verificar que sea del usuario
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar un producto (solo si pertenece al usuario)
    """
    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id  # Verificar que sea del usuario
    ).first()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado"
        )
    
    # Actualizar solo los campos enviados
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Eliminar un producto (solo si pertenece al usuario)
    """
    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id  # Verificar que sea del usuario
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marcar un producto como consumido (solo si pertenece al usuario)
    """
    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id  # Verificar que sea del usuario
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