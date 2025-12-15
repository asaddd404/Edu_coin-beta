# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

# 1. ENUMS (Роли и Статусы)
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "canceled"

# 2. ТАБЛИЦА ПОЛЬЗОВАТЕЛЕЙ
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default=UserRole.STUDENT)
    
    wallet_coins = Column(Integer, default=0)
    rating_points = Column(Integer, default=0)

    # Внешний ключ: В какой группе учится этот студент?
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    # СВЯЗИ:
    # 1. Группа, где он учится
    student_group = relationship("Group", foreign_keys=[group_id], back_populates="students")
    
    # 2. Группы, где он преподает (если это учитель)
    # Используем foreign_keys="Group.teacher_id", так как класс Group еще не определен полностью
    teaching_groups = relationship("Group", back_populates="teacher", foreign_keys="Group.teacher_id")

    # 3. Транзакции
    sent_transactions = relationship("Transaction", foreign_keys="Transaction.sender_id", back_populates="sender")
    received_transactions = relationship("Transaction", foreign_keys="Transaction.receiver_id", back_populates="receiver")
    
    # 4. Заказы в магазине
    orders = relationship("Order", back_populates="user")

# 3. ТАБЛИЦА ГРУПП
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    
    # Кто учитель этой группы?
    teacher_id = Column(Integer, ForeignKey("users.id"))

    # СВЯЗИ:
    # 1. Учитель этой группы
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teaching_groups")
    
    # 2. Ученики этой группы (ссылаемся на group_id в таблице User)
    students = relationship("User", foreign_keys="User.group_id", back_populates="student_group")

# 4. ТАБЛИЦА ТОВАРОВ
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    price = Column(Integer)
    quantity = Column(Integer)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

# 5. ТАБЛИЦА ЗАКАЗОВ
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id")) # Исправлено название таблицы товаров
    status = Column(String, default=OrderStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")
    product = relationship("Product")

# 6. ТАБЛИЦА ТРАНЗАКЦИЙ
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_transactions")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_transactions")

# 7. ТАБЛИЦА НАСТРОЕК (ЛИМИТЫ)
# Мы оставили только эту таблицу, SystemConfig удалили, так как это дубликат.
class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String, primary_key=True, index=True) # Например: "daily_limit"
    value = Column(Integer, default=100) # Например: 100