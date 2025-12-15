# test_db.py
from app.database import SessionLocal, engine
from sqlalchemy import text

def check_connection():
    print("🔌 Пробую подключиться к PostgreSQL...")
    try:
        # 1. Проверка соединения
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            print(f"✅ Успех! Версия базы: {result.fetchone()[0]}")

        # 2. Проверка записи
        db = SessionLocal()
        print("💾 Пробую сохранить тестовые данные...")
        try:
            # Делаем пустой коммит, чтобы проверить, работает ли механизм
            db.commit()
            print("✅ Коммит работает!")
        except Exception as e:
            print(f"❌ Ошибка коммита: {e}")
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        print("Проверь логин/пароль в database.py и запущен ли pgAdmin/Postgres!")

if __name__ == "__main__":
    check_connection()