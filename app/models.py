from sqlalchemy import Column, Integer, String, Boolean
from .database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class Token(Base):
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    token = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)

# Список филиалов для демонстрации
BRANCHES = [
    {"id": 1, "name": "Филиал МРМ"},
    {"id": 2, "name": "Филиал СЗ"},
    {"id": 3, "name": "Филиал Сибирь"},
    {"id": 4, "name": "Филиал ПВ"},
    {"id": 5, "name": "Филиал Юг"}
]
