# app/routers/transactions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from pydantic import BaseModel # Нам нужна простая схема для смены лимита
from app import schemas, models, database, oauth2

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions (Coins)"]
)

# Схема для изменения лимита (только тут нужна, поэтому опишем внутри)
class LimitUpdate(BaseModel):
    new_limit: int

# --- 1. АДМИН МЕНЯЕТ ЛИМИТ ---
@router.put("/config/limit")
def set_daily_limit(
    limit_data: LimitUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Только Админ может менять правила игры
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Только Админ может менять лимиты")
    
    # Ищем настройку в базе
    setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == "daily_limit").first()
    
    if not setting:
        # Если настройки еще нет - создаем
        setting = models.SystemSetting(key="daily_limit", value=limit_data.new_limit)
        db.add(setting)
    else:
        # Если есть - обновляем
        setting.value = limit_data.new_limit
        
    db.commit()
    return {"message": f"Новый дневной лимит установлен: {limit_data.new_limit}"}

# --- 2. ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ: УЗНАТЬ ЛИМИТ ---
def get_limit(db: Session):
    setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == "daily_limit").first()
    if setting:
        return setting.value
    return 10 # Если настройку еще не создали, по умолчанию будет 10

# --- 3. НАЧИСЛЕНИЕ КОИНОВ ---
@router.post("/", response_model=schemas.TransactionShow)
def give_coins(
    request: schemas.TransactionCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # А. Проверка прав
    if current_user.role not in [models.UserRole.TEACHER, models.UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Только учителя могут начислять коины!")

    if request.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя начислять коины самому себе!")

    # Б. ПОЛУЧАЕМ ТЕКУЩИЙ ЛИМИТ ИЗ БАЗЫ
    current_limit = get_limit(db)

    # В. Считаем, сколько уже дал сегодня
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    coins_given_today = db.query(func.sum(models.Transaction.amount))\
        .filter(models.Transaction.sender_id == current_user.id)\
        .filter(models.Transaction.receiver_id == request.receiver_id)\
        .filter(models.Transaction.created_at >= today_start)\
        .scalar() or 0
    
    # Г. Проверяем лимит
    if coins_given_today + request.amount > current_limit:
        left = current_limit - coins_given_today
        # Если left < 0, пишем 0
        left = max(0, left)
        raise HTTPException(
            status_code=400, 
            detail=f"Лимит исчерпан! Лимит школы: {current_limit}. Вы уже дали {coins_given_today}. Осталось: {left}"
        )

    # Д. Начисляем
    new_transaction = models.Transaction(
        sender_id=current_user.id,
        receiver_id=request.receiver_id,
        amount=request.amount,
        message=request.message
    )
    db.add(new_transaction)
    
    receiver = db.query(models.User).filter(models.User.id == request.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Ученик не найден")
        
    receiver.wallet_coins += request.amount
    receiver.rating_points += request.amount
    
    db.commit()
    db.refresh(new_transaction)
    return new_transaction