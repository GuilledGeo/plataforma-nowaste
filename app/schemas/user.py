"""
Schemas de Usuario
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema para crear usuario"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=200)


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema de respuesta de usuario"""
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema de token"""
    access_token: str
    token_type: str
    user: UserResponse