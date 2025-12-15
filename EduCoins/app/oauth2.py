# app/oauth2.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app import schemas, database, models
from app.routers import auth # Импортируем настройки (SECRET_KEY) отсюда

# Указываем, откуда брать токен (из URL /auth/login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Функция, которая достает текущего юзера по токену
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Расшифровываем токен
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 2. Ищем пользователя в БД
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
        
    return user # Возвращаем объект пользователя (User)