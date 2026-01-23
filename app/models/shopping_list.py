"""
INSTRUCCIONES: Crea nuevo archivo app/models/shopping_list.py
Modelo ShoppingList - Tabla para lista de compra automática
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ShoppingList(Base):
    """
    Modelo de Lista de Compra
    Tabla: shopping_list
    
    Se genera AUTOMÁTICAMENTE del menú semanal
    
    Flujo automático:
    =================
    1. Usuario crea menú: "Lunes Pasta Carbonara × 4 personas"
    2. Sistema calcula ingredientes:
       - Pasta: 400g (200g × 4/2)
       - Bacon: 200g (100g × 4/2)
    3. Compara con inventario:
       - Pasta en inventario: 500g → OK ✅
       - Bacon en inventario: 0g → FALTA 200g ❌
    4. Crea registros en ShoppingList para lo que FALTA
    5. Usuario ve lista: "Bacon - 200g - carnes - ❌"
    6. Usuario marca como comprado cuando lo compra
    7. Sistema actualiza inventario automáticamente
    """
    __tablename__ = "shopping_list"

    # Identificadores
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información del ingrediente a comprar
    ingredient_name = Column(String, nullable=False)  # "Bacon", "Tomate", etc
    category = Column(String, nullable=False)  # "meat", "vegetables", "dairy", etc
    
    # Cantidades necesarias
    quantity_needed = Column(Float, nullable=False)  # 200
    unit = Column(String, nullable=False)  # "g", "kg", "ml", "L", "units"
    
    # Relación con menú (opcional)
    # Si necesitas saber "esto vino del menú X"
    weekly_menu_id = Column(Integer, ForeignKey("weekly_menu.id"), nullable=True)
    
    # Estado de la compra
    is_bought = Column(Boolean, default=False)  # ¿Ya lo compré?
    bought_at = Column(DateTime, nullable=True)  # Cuándo
    
    # Información económica
    estimated_price = Column(Float, nullable=True)  # €15.50 (estimado)
    actual_price = Column(Float, nullable=True)  # €12.99 (lo que pagué)
    store = Column(String, nullable=True)  # "Mercadona", "Carrefour", etc
    
    # Notas
    notes = Column(String, nullable=True)  # "Marca: Barilla", "Sin gluten", etc
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="shopping_lists")

    def __repr__(self):
        status = "✅" if self.is_bought else "❌"
        return f"<ShoppingList({status} {self.ingredient_name} - {self.quantity_needed}{self.unit})>"