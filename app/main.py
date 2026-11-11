"""Точка входа FastAPI бэкенда ИС «Склад».

Запуск: uvicorn app.main:app --reload
Swagger UI: http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.db import init_db
from app.routers import categories, items


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # создаём таблицы при старте
    yield


app = FastAPI(title="ИС «Склад»", version="1.0.0", lifespan=lifespan)

app.include_router(items.router)
app.include_router(categories.router)


@app.get("/", tags=["status"])
def root():
    return {"status": "ok", "message": "ИС «Склад»: сервер работает"}
