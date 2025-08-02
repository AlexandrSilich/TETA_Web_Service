from passlib.context import CryptContext
from sqlalchemy.orm import Session
from . import models
import uuid

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функция для проверки пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Функция для хеширования пароля
def get_password_hash(password):
    return pwd_context.hash(password)

# Функция для создания пользователя
def create_user(db: Session, username: str, password: str):
    hashed_password = get_password_hash(password)
    db_user = models.User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Функция для аутентификации пользователя
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Функция для создания токена
def create_token(db: Session, user_id: int):
    token_value = str(uuid.uuid4())
    db_token = models.Token(user_id=user_id, token=token_value)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return token_value

# Функция для проверки токена
def verify_token(db: Session, token: str):
    db_token = db.query(models.Token).filter(models.Token.token == token, models.Token.is_active == True).first()
    if not db_token:
        return None
    return db_token.user_id

# Функция для удаления пользователя
def delete_user(db: Session, user_id: int):
    # Удаляем все токены пользователя
    db.query(models.Token).filter(models.Token.user_id == user_id).delete()
    
    # Удаляем пользователя
    db.query(models.User).filter(models.User.id == user_id).delete()
    
    db.commit()
    return True
