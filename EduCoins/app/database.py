# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Используем те же данные, что и в твоем успешном test_db.py
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/school_db"

print(f"🔌 Подключаюсь к PostgreSQL: {SQLALCHEMY_DATABASE_URL}")

# Для Postgres аргумент check_same_thread НЕ НУЖЕН, поэтому просто:
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()