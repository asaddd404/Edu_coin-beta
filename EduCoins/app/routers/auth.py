# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from jose import JWTError, jwt
from passlib.context import CryptContext
from app import schemas, models, database

router = APIRouter(tags=["Authentication"])

# СЕКРЕТНЫЙ КЛЮЧ (в реальном проекте хранить в .env!)
SECRET_KEY = "supersecretkey" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # Токен живет 1 день

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- ГЛАВНЫЙ ЭНДПОИНТ: ВХОД В СИСТЕМУ ---
@router.post("/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # 1. Ищем пользователя по логину
    print(f"📥 ПОПЫТКА ВХОДА:")
    print(f"   Логин: '{form_data.username}'")
    print(f"   Пароль: '{form_data.password}'")
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    # 2. Если пользователя нет ИЛИ пароль не подходит
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Если всё ок — генерируем токен
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role
    }