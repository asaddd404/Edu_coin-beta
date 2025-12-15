from app.database import SessionLocal
from app.models import User
from app.routers.auth import pwd_context

def reset_admin_password():
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()

    if admin:
        admin.hashed_password = pwd_context.hash("admin123") # <--- Твой новый пароль
        db.commit()
        print("✅ Пароль для admin успешно сброшен на 'admin123'")
    else:
        print("❌ Пользователь admin не найден!")

    db.close()

if __name__ == "__main__":
    reset_admin_password()