from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, auth, database
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str

class UserDelete(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    token: str
    token_type: str = "bearer"
    welcome_message: str

@router.post("/register", response_model=dict, summary="Регистрация нового пользователя", description="Регистрация нового пользователя. Логин не должен совпадать с текущими пользователями.")
def register(user: UserCreate, db: Session = Depends(database.get_db)):
    # Проверяем, существует ли пользователь
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    # Создаем пользователя
    auth.create_user(db, user.username, user.password)
    return {"message": "Пользователь успешно зарегистрирован"}

@router.post("/login", response_model=Token, summary="Операция логина в систему", description="Логин в систему под зарегистрированным ранее пользователем или под дефолтными пользователями указанными в описании. \nПосле успешного логина выдается Bear token.")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # Аутентифицируем пользователя
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Создаем токен
    token = auth.create_token(db, user.id)
    
    # Формируем приветственное сообщение
    welcome_message = f"Вы успешно залогинились в систему, {user.username}!"
    
    return {"token": token, "token_type": "bearer", "welcome_message": welcome_message}

@router.post("/delete-user", response_model=dict, summary="Удаления пользователя", description="Удаления пользователя из системы, используя логин и пароль данного пользователя.")
def delete_user(user: UserDelete, db: Session = Depends(database.get_db)):
    # Аутентифицируем пользователя
    authenticated_user = auth.authenticate_user(db, user.username, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Удаляем пользователя
    auth.delete_user(db, authenticated_user.id)
    
    return {"message": "Пользователь успешно удален"}
