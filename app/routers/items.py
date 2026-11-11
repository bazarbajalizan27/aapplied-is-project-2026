"""Маршруты для товаров: полный CRUD + фильтрация (ЛР №3-4)."""
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, col, select

from app.database.db import get_session
from app.database.models import Category, Item, ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("", response_model=List[ItemRead])
def read_items(
    session: SessionDep,
    search: Optional[str] = Query(default=None, description="Часть названия товара"),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    category_id: Optional[int] = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    """Список товаров с необязательной фильтрацией.

    Используются параметризованные запросы SQLModel (select/where),
    поэтому SQL-инъекции через search исключены.
    """
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price must be <= max_price")

    statement = select(Item)
    if search:
        statement = statement.where(col(Item.name).contains(search))
    if min_price is not None:
        statement = statement.where(Item.price >= min_price)
    if max_price is not None:
        statement = statement.where(Item.price <= max_price)
    if category_id is not None:
        statement = statement.where(Item.category_id == category_id)

    return session.exec(statement.offset(offset).limit(limit)).all()


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


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, item: ItemUpdate, session: SessionDep):
    """Частичное обновление: меняются только поля, переданные клиентом."""
    db_item = session.get(Item, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # exclude_unset — только реально присланные поля.
    # Явный null допустим лишь для supplier_id: остальные поля в БД NOT NULL.
    update_data = {
        key: value
        for key, value in item.model_dump(exclude_unset=True).items()
        if value is not None or key == "supplier_id"
    }
    new_category = update_data.get("category_id")
    if new_category is not None and session.get(Category, new_category) is None:
        raise HTTPException(status_code=404, detail="Category not found")

    db_item.sqlmodel_update(update_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_item(item_id: int, session: SessionDep):
    """Удалить товар. Сначала проверяем существование — иначе 404."""
    db_item = session.get(Item, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(db_item)
    session.commit()
    return {"message": f"Item {item_id} deleted successfully"}
