from fastapi import APIRouter, Depends, HTTPException, status, Header, Cookie, Response
from sqlalchemy.orm import Session
from .. import models, auth, database
from typing import List, Optional
import random
import uuid

router = APIRouter()

@router.get("/branches", response_model=List[dict], summary="Получить список филиалов", description="Возвращает список всех филиалов.")
def get_branches(
    response: Response,
    authorization: Optional[str] = Header(None), 
    db: Session = Depends(database.get_db)
):
    # Проверяем токен
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен авторизации отсутствует или неверный формат",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ")[1]
    user_id = auth.verify_token(db, token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Генерируем и устанавливаем cookie x_id_session
    session_id = str(uuid.uuid4())
    response.set_cookie(key="x_id_session", value=session_id, httponly=True)
    
    # Возвращаем список филиалов
    return models.BRANCHES

@router.get("/branches/{branch_id}/sim-cards", response_model=dict, summary="Получить количество доступных симкарт в конкретном филиале", description="Возвращает количество доступных симкарт в конкретном филиале.")
def get_branch_sim_cards(
    branch_id: int, 
    authorization: Optional[str] = Header(None),
    x_id_session: Optional[str] = Cookie(None),
    db: Session = Depends(database.get_db)
):
    # Проверяем токен
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен авторизации отсутствует или неверный формат",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ")[1]
    user_id = auth.verify_token(db, token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем наличие cookie x_id_session
    if not x_id_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отсутствует обязательный cookie x_id_session",
        )
    
    # Проверяем формат cookie x_id_session (должен быть UUID)
    try:
        uuid.UUID(x_id_session)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный формат cookie x_id_session",
        )
    
    # Проверяем существование филиала
    branch = next((b for b in models.BRANCHES if b["id"] == branch_id), None)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Филиал с ID {branch_id} не найден",
        )
    
    # Генерируем случайное количество сим-карт
    sim_cards_count = random.randint(20000, 100000)
    
    return {
        "branch_id": branch_id,
        "branch_name": branch["name"],
        "available_sim_cards": sim_cards_count,
        "session_id": x_id_session
    }
