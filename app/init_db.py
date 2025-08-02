from sqlalchemy.orm import Session
from . import models, auth, database

# Функция для создания пользователей по умолчанию
def create_default_users():
    db = database.SessionLocal()
    try:
        # Создаем 10 пользователей по умолчанию
        for i in range(1, 11):
            username = f"demouser{i}"
            password = f"Password{i}"
            
            # Проверяем, существует ли пользователь
            existing_user = db.query(models.User).filter(models.User.username == username).first()
            if not existing_user:
                # Создаем пользователя
                auth.create_user(db, username, password)
                print(f"Пользователь '{username}' успешно создан")
            else:
                print(f"Пользователь '{username}' уже существует")
    finally:
        db.close()
