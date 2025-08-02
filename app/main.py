from fastapi import FastAPI
from .routes import auth, branches
from .database import engine, Base
from .init_db import create_default_users

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем пользователей по умолчанию
create_default_users()

# Создаем экземпляр FastAPI с настройками документации
app = FastAPI(
    title="TETA Web Service Load Testing",
    description="""
    Учебный веб-сервис для отладки HTTP-скриптов.
    
    ## Функциональность
    
    Сервис предоставляет следующие возможности:
    
    1. **Регистрация и авторизация пользователей** - создание учетных записей и получение токенов доступа
    2. **Работа с филиалами** - получение списка филиалов и информации о доступных сим-картах
    3. **Работа с различными типами параметров запросов**:
       - Параметры в URL
       - Заголовки (Headers)
       - Токены авторизации
       - Cookie-параметры
    
    ## Учебные цели
    
    Данный сервис помогает изучить:
    - Выполнение GET и POST запросов
    - Авторизацию с использованием токенов
    - Передачу параметров в заголовках
    - Работу с cookie
    - Обработку ошибок
    
    ## Учетные данные по умолчанию
    
    Для тестирования API можно использовать следующие учетные данные:
    - Пользователи: demouser1, demouser2, ..., demouser10
    - Пароли: Password1, Password2, ..., Password10
    
    Например:
    - Логин: demouser1, Пароль: Password1
    - Логин: demouser2, Пароль: Password2
    - и т.д.
    """,
    version="1.0.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# Подключаем маршруты
app.include_router(auth.router, tags=["Аутентификация"])
app.include_router(branches.router, tags=["Филиалы"])

@app.get("/", tags=["Информация"])
def read_root():
    return {
        "message": "Добро пожаловать в учебный веб-сервис для отладки HTTP-скриптов",
        "docs": "/docs",
        "default_users": "Доступны пользователи demouser1-demouser10 с паролями Password1-Password10"
    }
