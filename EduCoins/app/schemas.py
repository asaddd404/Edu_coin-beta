# app/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .models import UserRole, OrderStatus

# --- СХЕМЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ (Сначала они!) ---
class UserBase(BaseModel):
    username: str
    full_name: str
    role: UserRole = UserRole.STUDENT

class UserCreate(UserBase):
    password: str
    group_id: Optional[int] = None 
    role: str = "student" # <--- Убедись, что можно передать роль (или она есть в UserBase)

class UserShow(UserBase):
    id: int
    wallet_coins: int
    rating_points: int
    group_id: Optional[int]
    
    class Config:
        from_attributes = True

# --- СХЕМЫ ДЛЯ ТОКЕНА (Теперь можно использовать UserShow) ---
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str 
    user: UserShow # <-- Теперь Python знает, что такое UserShow
    
class TokenData(BaseModel):
    username: Optional[str] = None

# --- СХЕМЫ ДЛЯ ГРУПП ---
class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    teacher_id: int

class Group(GroupBase):
    id: int
    teacher_id: int
    
    class Config:
        from_attributes = True

# --- СХЕМЫ ДЛЯ ТРАНЗАКЦИЙ ---
class TransactionCreate(BaseModel):
    receiver_id: int
    amount: int
    message: Optional[str] = "Награда"

class TransactionShow(BaseModel):
    id: int
    amount: int
    message: Optional[str]
    created_at: datetime
    sender_id: int
    receiver_id: int
    
    class Config:
        from_attributes = True

# --- СХЕМЫ ДЛЯ ТОВАРОВ ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    quantity: int
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductShow(ProductBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True