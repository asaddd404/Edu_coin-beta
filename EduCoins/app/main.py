# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware # <--- Для CORS
from fastapi.exceptions import RequestValidationError # <--- Вот этот импорт ты забыл!
from fastapi.responses import JSONResponse
from app.database import engine
from app import models
# Импортируем наши роутеры
from app.routers import auth, users, transactions, shop
# Если ты уже создал groups.py, раскомментируй строку ниже:
# from app.routers import groups 

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="EduCoins System")

# --- НАСТРОЙКА CORS (Разрешаем всё) ---
app.add_middleware(
    CORSMiddleware,
    # Разрешаем запросы с любых сайтов (фронтенд на 8080, 5173 и т.д.)
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], # Разрешаем любые методы (GET, POST, OPTIONS и т.д.)
    allow_headers=["*"], # Разрешаем любые заголовки
)

# --- РОУТЕРЫ ---
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(shop.router)
# app.include_router(groups.router) # Раскомментируй, если файл groups.py существует

# --- ЛОВЕЦ ОШИБОК ВАЛИДАЦИИ ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"\n❌ ОШИБКА ВАЛИДАЦИИ ДАННЫХ (422)!")
    print(f"➡️ Клиент отправил тело: {exc.body}")
    print(f"➡️ Детали ошибок: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(exc.body)},
    )

@app.get("/")
def read_root():
    return {"message": "System is running!"}