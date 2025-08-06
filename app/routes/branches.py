from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .. import models, auth, database
from typing import List, Optional
import random
import uuid

router = APIRouter()

# Создаем схему безопасности HTTPBearer
security = HTTPBearer(description="Введите Bearer токен, полученный при логине")

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(database.get_db)
):
    """
    Получить ID текущего пользователя по токену.
    
    Args:
        credentials: Учетные данные Authorization Bearer
        db: Сессия базы данных
        
    Returns:
        int: ID пользователя
        
    Raises:
        HTTPException: Если токен недействителен
    """
    token = credentials.credentials
    user_id = auth.verify_token(db, token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id

@router.get(
    "/branches", 
    response_model=dict, 
    summary="Получить список филиалов",
    description="Возвращает список всех филиалов. В хедере запроса необходимо использовать Authorization: Bearer {token}, полученный при выполнении операции логина  или в swagger авторизоваться через кнопку Authorize"
)
def get_branches(
    response: Response,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Получить список всех доступных филиалов.
    
    Эндпоинт требует авторизации через Bearer token.
    
    Для тестирования в Swagger UI:
    1. Выполните POST /login для получения токена
    2. Нажмите кнопку "Authorize" (замок) в правом верхнем углу Swagger UI
    3. Введите полученный токен БЕЗ слова "Bearer" (только сам токен)
    4. Нажмите "Authorize" в модальном окне
    5. Выполните данный запрос
    6. Скопируйте session_id из ответа для использования в следующем запросе
    
    Args:
        response: Объект Response для установки cookie
        current_user_id: ID текущего авторизованного пользователя
        
    Returns:
        dict: Список филиалов и session_id для следующего запроса
    """
    # Генерируем session ID
    session_id = str(uuid.uuid4())
    
    # Устанавливаем cookie (для браузера)
    response.set_cookie(key="x_id_session", value=session_id, httponly=False)
    
    # Возвращаем список филиалов и session_id в теле ответа для удобства тестирования
    return {
        "branches": models.BRANCHES,
        "session_id": session_id,
        "message": "Для следующего запроса /branches/{branch_id}/sim-cards используйте session_id из этого ответа в поле x_id_session cookie"
    }

@router.get(
    "/branches/{branch_id}/sim-cards", 
    response_model=dict,
    summary="Получить количество доступных симкарт в конкретном филиале",
    description="Возвращает количество доступных симкарт в конкретном филиале. В хедере запроса необходимо использовать Authorization: Bearer {token}, полученный при выполнении операции логина, а в cookie необходимо передавать x_id_session, полученный в предыдущем запросе /branches"
)
def get_branch_sim_cards(
    branch_id: int, 
    x_id_session: Optional[str] = Cookie(None),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Получить информацию о доступных сим-картах в конкретном филиале.
    
    Эндпоинт требует:
    1. Авторизации через Bearer token (используйте кнопку "Authorize")
    2. Cookie x_id_session, полученное из запроса /branches
    
    Для тестирования в Swagger UI:
    1. Сначала авторизуйтесь через кнопку "Authorize"
    2. Выполните GET /branches и скопируйте session_id из ответа
    3. В этом запросе в поле x_id_session (cookie) вставьте скопированное значение
    4. Выполните запрос
    
    Args:
        branch_id: ID филиала (1-5)
        x_id_session: Session ID из cookie (получите из предыдущего запроса /branches)
        current_user_id: ID текущего авторизованного пользователя
        
    Returns:
        dict: Информация о филиале и количестве доступных сим-карт
        
    Raises:
        HTTPException: Если отсутствует cookie, некорректный формат cookie или филиал не найден
    """
    # Проверяем наличие cookie x_id_session
    if not x_id_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отсутствует обязательный cookie x_id_session. Сначала выполните запрос GET /branches и скопируйте session_id из ответа",
        )
    
    # Проверяем формат cookie x_id_session (должен быть UUID)
    try:
        uuid.UUID(x_id_session)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный формат cookie x_id_session. Используйте session_id из ответа /branches",
        )
    
    # Проверяем существование филиала
    branch = next((b for b in models.BRANCHES if b["id"] == branch_id), None)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Филиал с ID {branch_id} не найден. Доступные филиалы: 1-5",
        )
    
    # Генерируем случайное количество сим-карт для демонстрации
    sim_cards_count = random.randint(20000, 100000)
    
    return {
        "branch_id": branch_id,
        "branch_name": branch["name"],
        "available_sim_cards": sim_cards_count,
        "session_id": x_id_session
    }
