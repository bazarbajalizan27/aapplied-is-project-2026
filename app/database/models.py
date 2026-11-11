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
    transactions: List["StockTransaction"] = Relationship(back_populates="item")


class StockTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id")
    quantity_change: int  # +приход / -расход
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    item: Optional[Item] = Relationship(back_populates="transactions")
