"""Маршруты для категорий (нужны фронтенду для выпадающего списка)."""
from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database.db import get_session
from app.database.models import Category, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("", response_model=List[CategoryRead])
def read_categories(session: SessionDep):
    return session.exec(select(Category)).all()
