"""
API Endpoint para escaneo de tickets
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import tempfile

from app.database import get_db
from app.models.user import User
from app.models.product import Product, ProductStatus
from app.services.ticket_scanner_service import TicketScannerService
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/scan")
async def scan_ticket(
    file: UploadFile = File(...),
    auto_import: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Escanear ticket de compra y extraer productos automáticamente
    
    - **file**: Imagen del ticket (JPG, PNG)
    - **auto_import**: Si True, importa automáticamente al inventario
    
    **Returns:** Lista de productos detectados con categorías y fechas de caducidad
    """
    
    # Validar archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "El archivo debe ser una imagen")
    
    # Guardar temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Procesar ticket
        scanner = TicketScannerService()
        result = scanner.process_ticket(tmp_path)
        
        # Auto-importar si está activado
        created_products = []
        if auto_import:
            for product_data in result["products"]:
                db_product = Product(
                    user_id=current_user.id,
                    name=product_data["name"],
                    category=product_data["category"],
                    store=product_data["store"],
                    price=product_data["price"],
                    quantity=product_data["quantity"],
                    unit=product_data["unit"],
                    location=product_data["location"],
                    purchase_date=product_data["purchase_date"],
                    expiration_date=product_data["expiration_date"],
                    notes=product_data["notes"],
                    status=ProductStatus.ACTIVE
                )
                db.add(db_product)
                created_products.append(product_data["name"])
            
            db.commit()
        
        # Limpiar
        os.unlink(tmp_path)
        
        return {
            **result,
            "auto_imported": auto_import,
            "created_products": created_products if auto_import else []
        }
    
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        raise HTTPException(500, f"Error al procesar ticket: {str(e)}")