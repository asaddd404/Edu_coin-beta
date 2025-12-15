# app/check_login.py
from app.database import SessionLocal
from app.models import User
from app.routers.auth import verify_password, pwd_context

def test_login():
    db = SessionLocal()
    print("--- НАЧАЛО ПРОВЕРКИ ---")
    
    # 1. Ищем пользователя
    user = db.query(User).filter(User.username == "admin").first()
    
    if not user:
        print("❌ ОШИБКА: Пользователь 'admin' НЕ НАЙДЕН в базе данных!")
        return

    print(f"✅ Пользователь найден: {user.username}")
    print(f"🔑 Хеш пароля в базе: {user.hashed_password}")

    # 2. Проверяем пароль
    password_to_check = "admin123"
    is_valid = verify_password(password_to_check, user.hashed_password)

    if is_valid:
        print(f"✅ УСПЕХ: Пароль '{password_to_check}' подходит!")
        print("Значит, проблема в Фронтенде или Браузере.")
    else:
        print(f"❌ ОШИБКА: Пароль '{password_to_check}' НЕ ПОДХОДИТ!")
        print("Значит, проблема в Базе Данных или хешировании.")
        
        # Тест хеширования
        print("\n--- Тест создания хеша ---")
        try:
            new_hash = pwd_context.hash("test")
            print(f"Тестовый хеш создается: {new_hash[:20]}...")
        except Exception as e:
            print(f"Ошибка библиотеки хеширования: {e}")

    db.close()

if __name__ == "__main__":
    test_login()