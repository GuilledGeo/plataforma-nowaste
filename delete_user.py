"""
Borrar usuario para recrearlo
"""
from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    user = db.query(User).filter(User.email == "guilled18@freshkeep.com").first()
    if user:
        db.delete(user)
        db.commit()
        print(f"✅ Usuario {user.email} eliminado")
    else:
        print("❌ Usuario no encontrado")
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()