"""ORM-модели SQLModel для ИС «Склад» (ЛР №2)."""
from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    # Связь: у одной категории много товаров
    items: List["Item"] = Relationship(back_populates="category")


class Supplier(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    phone: Optional[str] = None
    email: Optional[str] = None

    # Связь: у одного поставщика много товаров
    items: List["Item"] = Relationship(back_populates="supplier")


class ItemBase(SQLModel):
    """Общие поля товара. Не является таблицей — на его основе строятся схемы API."""
    name: str = Field(index=True, min_length=1)
    price: float = Field(ge=0)
    quantity: int = Field(default=0, ge=0)
    category_id: int = Field(foreign_key="category.id")
    supplier_id: Optional[int] = Field(default=None, foreign_key="supplier.id")


class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    category: Optional[Category] = Relationship(back_populates="items")
    supplier: Optional[Supplier] = Relationship(back_populates="items")
    # При удалении товара удаляем и его журнал транзакций (иначе item_id NOT NULL нарушится)
    transactions: List["StockTransaction"] = Relationship(
        back_populates="item",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ItemCreate(ItemBase):
    """Схема для POST: клиент не может передать id."""


class ItemUpdate(SQLModel):
    """Схема для PATCH: все поля необязательные — клиент шлёт только то, что меняет."""
    name: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, ge=0)
    quantity: Optional[int] = Field(default=None, ge=0)
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None


class ItemRead(ItemBase):
    """Схема ответа API: товар вместе с id."""
    id: int


class CategoryRead(SQLModel):
    id: int
    name: str


class StockTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id")
    quantity_change: int  # +приход / -расход
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    item: Optional[Item] = Relationship(back_populates="transactions")
