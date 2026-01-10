"""
Script para crear las tablas de la base de datos y usuario por defecto
"""
from app.database import Base, engine, SessionLocal
from app.models import User, Product, Recipe, Notification
from datetime import datetime

print("="*60)
print("INICIANDO CREACIÓN DE BASE DE DATOS")
print("="*60)

# Crear todas las tablas
print("\n1. Creando tablas...")
Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas exitosamente!")

print("\nTablas creadas:")
for table in Base.metadata.sorted_tables:
    print(f"  - {table.name}")

# Hash pre-calculado de "Papelera1234"
HASHED_PASSWORD = "$2b$12$EixZaYVK1fsbw1ZfbX3OXe/mXCLPB4V8cxRY8eKmJnBPaK8bXRPuC"

# Crear usuario por defecto
print("\n2. Verificando usuario por defecto...")
db = SessionLocal()
try:
    # Buscar usuario por email
    existing_user = db.query(User).filter(User.email == "guilled18@freshkeep.com").first()
    
    if existing_user:
        print(f"✅ Usuario ya existe:")
        print(f"   - ID: {existing_user.id}")
        print(f"   - Email: {existing_user.email}")
        print(f"   - Nombre: {existing_user.full_name}")
    else:
        print("📝 Creando usuario guilled18...")
        # Crear usuario guilled18
        default_user = User(
            email="guilled18@freshkeep.com",
            full_name="Guilled",
            hashed_password=HASHED_PASSWORD,
            is_active=True,
            is_superuser=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
        
        print("✅ Usuario creado exitosamente!")
        print(f"   - ID: {default_user.id}")
        print(f"   - Email: guilled18@freshkeep.com")
        print(f"   - Contraseña: Papelera1234")
        print(f"   - Nombre: {default_user.full_name}")
        
except Exception as e:
    print(f"❌ Error al crear usuario: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n" + "="*60)
print("✅ PROCESO COMPLETADO")
print("="*60)