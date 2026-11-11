"""Настройка подключения к БД (ЛР №2)."""
import os

from sqlmodel import SQLModel, create_engine

# Импорт моделей нужен, чтобы SQLModel "увидел" все таблицы перед create_all
from app.database import models  # noqa: F401

sqlite_url = "sqlite:///database.db"

# echo=True выводит SQL-логи в консоль (отключить: SQL_ECHO=0)
engine = create_engine(
    sqlite_url,
    echo=os.getenv("SQL_ECHO", "1") == "1",
    connect_args={"check_same_thread": False},  # нужно для SQLite при работе с FastAPI
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
