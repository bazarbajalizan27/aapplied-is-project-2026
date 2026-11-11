"""Наполнение БД тестовыми данными (ЛР №2). Запуск: python seed.py"""
from sqlmodel import Session, select

from app.database.db import engine, init_db
from app.database.models import Category, Item, StockTransaction, Supplier


def seed() -> None:
    init_db()
    with Session(engine) as session:
        if session.exec(select(Category)).first():
            print("База уже содержит данные — seed пропущен.")
            return

        categories = [
            Category(name="Электроника"),
            Category(name="Мебель"),
            Category(name="Канцелярия"),
            Category(name="Инструменты"),
        ]
        suppliers = [
            Supplier(name="TechImport LLP", phone="+7 701 111 22 33", email="sales@techimport.kz"),
            Supplier(name="Astana Mebel", phone="+7 702 222 33 44", email="info@astanamebel.kz"),
            Supplier(name="OfficePro", phone="+7 705 333 44 55", email="order@officepro.kz"),
        ]
        session.add_all(categories + suppliers)
        session.commit()
        for obj in categories + suppliers:
            session.refresh(obj)

        items = [
            Item(name="Laptop Lenovo ThinkPad", price=650000, quantity=12,
                 category_id=categories[0].id, supplier_id=suppliers[0].id),
            Item(name="Monitor Samsung 27", price=145000, quantity=30,
                 category_id=categories[0].id, supplier_id=suppliers[0].id),
            Item(name="Office Chair Ergo", price=89000, quantity=25,
                 category_id=categories[1].id, supplier_id=suppliers[1].id),
            Item(name="Notebook A4 (pack of 10)", price=3500, quantity=200,
                 category_id=categories[2].id, supplier_id=suppliers[2].id),
            Item(name="Cordless Drill Bosch", price=52000, quantity=8,
                 category_id=categories[3].id, supplier_id=None),
        ]
        session.add_all(items)
        session.commit()
        for it in items:
            session.refresh(it)

        transactions = [
            StockTransaction(item_id=items[0].id, quantity_change=15, comment="Первичная поставка"),
            StockTransaction(item_id=items[0].id, quantity_change=-3, comment="Отгрузка клиенту"),
            StockTransaction(item_id=items[1].id, quantity_change=30, comment="Первичная поставка"),
            StockTransaction(item_id=items[3].id, quantity_change=200, comment="Закупка канцелярии"),
            StockTransaction(item_id=items[4].id, quantity_change=-2, comment="Списание (брак)"),
        ]
        session.add_all(transactions)
        session.commit()
        print("Тестовые данные добавлены: "
              f"{len(categories)} категорий, {len(suppliers)} поставщика, "
              f"{len(items)} товаров, {len(transactions)} транзакций.")


if __name__ == "__main__":
    seed()
