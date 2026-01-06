"""
Script para crear las tablas de la base de datos
"""
from app.database import Base, engine
from app.models import User, Product, Recipe, Notification

print("Creando tablas en la base de datos...")

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

print("✅ Tablas creadas exitosamente!")
print("\nTablas creadas:")
for table in Base.metadata.sorted_tables:
    print(f"  - {table.name}")