"""
Utilidades de autenticación
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.config import settings

# Configuración
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funciones de password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashear password"""
    return pwd_context.hash(password)

# Funciones de JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear JWT token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

# 🔥 NUEVA VERSIÓN - Usar Header en lugar de HTTPBearer
def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtener usuario actual desde el token JWT
    Usa Header en lugar de HTTPBearer para evitar problemas de CORS/403
    """
    
    print("=" * 60)
    print("🚀 get_current_user ejecutándose")
    print(f"📥 Authorization header: {authorization[:50] if authorization else 'None'}...")
    
    if not authorization:
        print("❌ No hay Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer el token del formato "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            print(f"❌ Scheme incorrecto: {scheme}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Esquema de autenticación inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        print("❌ Formato de Authorization header inválido")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"🔑 Token extraído: {token[:30]}...")
    print(f"🔐 SECRET_KEY: {settings.SECRET_KEY[:20]}...")
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        print(f"✅ Token decodificado. User ID: {user_id}")
        
        if user_id is None:
            print("❌ User ID es None en el payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: no contiene user ID"
            )
            
    except JWTError as e:
        print(f"❌ JWTError: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"No se pudo validar las credenciales: {str(e)}"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        print(f"❌ Usuario con ID {user_id} NO encontrado en BD")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if not user.is_active:
        print(f"❌ Usuario {user.email} está inactivo")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    print(f"✅ Usuario autenticado exitosamente: {user.email}")
    print("=" * 60)
    return user