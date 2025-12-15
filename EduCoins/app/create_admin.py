# app/create_admin.py

# 1. ОБРАТИ ВНИМАНИЕ: Мы добавили 'app.' перед database и models
from app.database import SessionLocal
from app.models import User, UserRole

# Passlib - это внешняя библиотека, ей 'app.' не нужен
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_super_admin():
    db = SessionLocal()
    
    # Проверяем, есть ли админ
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        print("❌ Админ уже существует!")
        db.close()
        return

    # Создаем админа
    new_admin = User(
        username="admin",
        hashed_password=pwd_context.hash("admin123"), # Пароль
        full_name="Super Director",
        role=UserRole.ADMIN,
        wallet_coins=999999,
        rating_points=999999
    )
    
    db.add(new_admin)
    db.commit()
    print("✅ Супер-Админ успешно создан!")
    print("Логин: admin")
    print("Пароль: admin123")
    
    db.close()

if __name__ == "__main__":
    create_super_admin()