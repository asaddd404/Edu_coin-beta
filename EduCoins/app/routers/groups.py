from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import database, models, schemas, oauth2

router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)

# 1. Получить все группы (для списка)
@router.get("/", response_model=List[schemas.Group])
def read_groups(db: Session = Depends(database.get_db)):
    return db.query(models.Group).all()

# 2. Создать группу (Только админ или учитель)
@router.post("/", response_model=schemas.Group)
def create_group(
    group: schemas.GroupCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Проверка: группу с таким именем нельзя дублировать
    existing = db.query(models.Group).filter(models.Group.name == group.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Группа с таким именем уже есть")

    new_group = models.Group(name=group.name, teacher_id=group.teacher_id)
    db.add(new_group)
    db.commit() # <--- ВАЖНО!
    db.refresh(new_group)
    return new_group

# 3. Получить студентов конкретной группы
@router.get("/{group_id}/students", response_model=List[schemas.UserShow])
def get_students_in_group(group_id: int, db: Session = Depends(database.get_db)):
    students = db.query(models.User).filter(models.User.group_id == group_id).all()
    return students