from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ВАЖНО: Замени 'postgres' и '1234' на ТВОЙ логин и пароль от pgAdmin!
# Если у тебя пароль пустой, напиши просто password
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/school_db"

# Создаем движок подключения
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем сессию (через неё мы будем слать запросы)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция, которая выдает базу данных при запросе
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()