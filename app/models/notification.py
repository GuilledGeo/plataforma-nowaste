"""
Modelo Notification - Tabla de Notificaciones
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class NotificationType(str, enum.Enum):
    """Tipos de notificación"""
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    LOW_STOCK = "low_stock"
    RECIPE_SUGGESTION = "recipe_suggestion"


class Notification(Base):
    """
    Modelo de Notificación
    Tabla: notifications
    """
    __tablename__ = "notifications"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    
    # Contenido
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    
    # Estado
    is_read = Column(Integer, default=0)  # Boolean: 1=True, 0=False
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.type}, read={self.is_read})>"
