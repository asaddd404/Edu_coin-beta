# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models, database, oauth2
from app.routers.auth import pwd_context # Берем хешировалку паролей
from sqlalchemy import desc
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# 1. РЕГИСТРАЦИЯ (Доступна всем)
@router.post("/", response_model=schemas.UserShow)
def create_user(request: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Проверяем, не занят ли логин
    existing_user = db.query(models.User).filter(models.User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Хешируем пароль
    hashed_pass = pwd_context.hash(request.password)
    
    # Создаем юзера
    new_user = models.User(
        username=request.username,
        full_name=request.full_name,
        hashed_password=hashed_pass,
        role=request.role,
        group_id=request.group_id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 2. ПОЛУЧИТЬ СВОЙ ПРОФИЛЬ (Нужен токен!)
@router.get("/me", response_model=schemas.UserShow)
def read_users_me(current_user: models.User = Depends(oauth2.get_current_user)):
    return current_user

# 3. ПОЛУЧИТЬ СПИСОК УЧЕНИКОВ (Только для Учителей и Админов)
@router.get("/students", response_model=List[schemas.UserShow])
def read_all_students(
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Проверка прав: Студент не должен видеть список всех других
    if current_user.role == models.UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    students = db.query(models.User).filter(models.User.role == models.UserRole.STUDENT).all()
    return students


# 4. ЛИДЕРБОРД (ТОП-10 Учеников)
@router.get("/leaderboard", response_model=List[schemas.UserShow])
def get_leaderboard(db: Session = Depends(database.get_db)):
    # Берем всех со стусом STUDENT
    # Сортируем по rating_points (от большего к меньшему)
    # Берем только первых 10
    top_students = db.query(models.User)\
        .filter(models.User.role == models.UserRole.STUDENT)\
        .order_by(desc(models.User.rating_points))\
        .limit(10)\
        .all()
    
    return top_students