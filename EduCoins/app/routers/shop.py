# app/routers/shop.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models, database, oauth2

router = APIRouter(
    prefix="/shop",
    tags=["Shop & Orders"]
)

# 1. СОЗДАТЬ ТОВАР (Только Админ или Менеджер)
@router.post("/items", response_model=schemas.ProductShow)
def create_item(
    request: schemas.ProductCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Нет прав на добавление товаров")

    new_item = models.Product(
        name=request.name,
        description=request.description,
        price=request.price,
        quantity=request.quantity,
        image_url=request.image_url
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# 2. СПИСОК ТОВАРОВ (Видят все)
@router.get("/items", response_model=List[schemas.ProductShow])
def get_items(db: Session = Depends(database.get_db)):
    # Показываем только активные товары, которых больше 0 на складе
    items = db.query(models.Product).filter(models.Product.is_active == True).all()
    return items

# 3. КУПИТЬ ТОВАР (Только Ученик)
@router.post("/buy/{item_id}")
def buy_item(
    item_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # А. Проверка прав
    if current_user.role != models.UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Покупать могут только ученики")

    # Б. Ищем товар
    item = db.query(models.Product).filter(models.Product.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Товар закончился :(")

    # В. Проверка денег
    if current_user.wallet_coins < item.price:
        raise HTTPException(status_code=400, detail="Недостаточно коинов")

    # Г. СОВЕРШАЕМ ПОКУПКУ (Транзакция)
    # 1. Списываем деньги
    current_user.wallet_coins -= item.price
    # 2. Уменьшаем склад
    item.quantity -= 1
    # 3. Создаем заказ
    new_order = models.Order(
        user_id=current_user.id,
        product_id=item.id,
        status=models.OrderStatus.WAITING # Сразу статус "Ждет подтверждения"
    )
    
    db.add(new_order)
    db.commit()
    
    return {"message": f"Вы успешно купили {item.name}! Подойдите к менеджеру."}