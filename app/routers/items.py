"""Маршруты для товаров (ЛР №3: GET и POST)."""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database.db import get_session
from app.database.models import Category, Item, ItemCreate, ItemRead

router = APIRouter(prefix="/items", tags=["items"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("", response_model=List[ItemRead])
def read_items(session: SessionDep):
    """Вернуть список всех товаров."""
    return session.exec(select(Item)).all()


@router.get("/{item_id}", response_model=ItemRead)
def read_item(item_id: int, session: SessionDep):
    """Найти товар по ID или вернуть 404."""
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, session: SessionDep):
    """Создать товар. Валидация (цена >= 0, непустое название) выполняется автоматически."""
    if session.get(Category, item.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
