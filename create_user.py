"""
Script para crear tu usuario con bcrypt 4.1.2
"""
from app.database import SessionLocal
from app.models.user import User
from app.utils.auth import get_password_hash
from datetime import datetime

print("Creando usuario guilled18...")

db = SessionLocal()
try:
    # Verificar si ya existe
    existing_user = db.query(User).filter(User.email == "guilled18@freshkeep.com").first()
    
    if existing_user:
        print("❌ El usuario ya existe, bórralo primero con delete_user.py")
    else:
        # Crear usuario con hash correcto
        new_user = User(
            email="guilled18@freshkeep.com",
            full_name="Guilled",
            hashed_password=get_password_hash("Papelera1234"),  # Hash en tiempo real
            is_active=True,
            is_superuser=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Usuario creado exitosamente!")
        print(f"   ID: {new_user.id}")
        print(f"   Email: guilled18@freshkeep.com")
        print(f"   Contraseña: Papelera1234")
        print(f"   Nombre: {new_user.full_name}")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()