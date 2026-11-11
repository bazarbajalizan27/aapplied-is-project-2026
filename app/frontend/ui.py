"""Веб-интерфейс ИС «Склад» на Streamlit (ЛР №5).

Запуск (бэкенд FastAPI должен быть запущен на порту 8000):
    streamlit run app/frontend/ui.py
"""
import pandas as pd
import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 5

st.set_page_config(page_title="ИС «Склад»", page_icon="📦", layout="wide")


# ---------- Функции работы с API ----------
def api_get(path: str, params: dict | None = None):
    response = requests.get(f"{BASE_URL}{path}", params=params, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_items(search: str = "", min_price: float = 0.0, max_price: float | None = None) -> list[dict]:
    params: dict = {}
    if search:
        params["search"] = search
    if min_price > 0:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price
    return api_get("/items", params)


def fetch_categories() -> list[dict]:
    return api_get("/categories")


# ---------- Заголовок и боковая панель ----------
st.title("📦 ИС «Склад» — учёт товаров")
st.write("Клиентская часть системы: данные берутся у FastAPI-бэкенда по HTTP.")

with st.sidebar:
    st.header("О проекте")
    st.write(
        "**Стек:** FastAPI + SQLModel (бэкенд), Streamlit (интерфейс).\n\n"
        "Лабораторные работы №1–5."
    )
    st.caption(f"Адрес бэкенда: {BASE_URL}")
    st.divider()

# ---------- Проверка доступности бэкенда ----------
try:
    categories = fetch_categories()
except requests.exceptions.RequestException:
    st.error(
        "Не удаётся подключиться к бэкенду. Запустите сервер командой "
        "`uvicorn app.main:app --reload` и обновите страницу."
    )
    st.stop()

category_names = {c["id"]: c["name"] for c in categories}

# ---------- Форма добавления (выполняется ДО таблицы, чтобы новая строка появилась сразу) ----------
with st.sidebar:
    st.header("➕ Новый товар")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Название")
        price = st.number_input("Цена", min_value=0.0, step=100.0)
        quantity = st.number_input("Количество", min_value=0, step=1)
        category = st.selectbox(
            "Категория", options=categories, format_func=lambda c: c["name"]
        )
        submitted = st.form_submit_button("Сохранить")

    if submitted:
        payload = {
            "name": name.strip(),
            "price": price,
            "quantity": int(quantity),
            "category_id": category["id"],
        }
        try:
            response = requests.post(f"{BASE_URL}/items", json=payload, timeout=TIMEOUT)
            if response.status_code == 201:
                st.success(f"Товар «{payload['name']}» добавлен!")
            elif response.status_code == 422:
                st.error("Проверьте данные: название не должно быть пустым, цена — отрицательной.")
            else:
                st.error(f"Ошибка сервера: {response.status_code} {response.text}")
        except requests.exceptions.RequestException:
            st.error("Бэкенд недоступен.")

# ---------- Поиск и фильтры ----------
st.subheader("Список товаров")
col_search, col_min, col_max = st.columns([3, 1, 1])
search_query = col_search.text_input("🔍 Поиск по названию")
min_price = col_min.number_input("Цена от", min_value=0.0, value=0.0, step=1000.0)
max_price_value = col_max.number_input("Цена до (0 — без ограничения)", min_value=0.0, value=0.0, step=1000.0)

try:
    items = fetch_items(
        search=search_query,
        min_price=min_price,
        max_price=max_price_value if max_price_value > 0 else None,
    )
except requests.exceptions.HTTPError as exc:
    st.error(f"Ошибка запроса: {exc.response.status_code} {exc.response.text}")
    items = []
except requests.exceptions.RequestException:
    st.error("Бэкенд недоступен.")
    items = []

if items:
    df = pd.DataFrame(items)
    df["category"] = df["category_id"].map(category_names)
    df = df[["id", "name", "price", "quantity", "category"]]
    df.columns = ["ID", "Название", "Цена", "Остаток", "Категория"]
    st.dataframe(df, hide_index=True)
    st.caption(f"Найдено товаров: {len(df)}")
else:
    st.info("Товары не найдены.")

# ---------- Удаление ----------
if items:
    with st.sidebar:
        st.divider()
        st.header("🗑️ Удалить товар")
        to_delete = st.selectbox(
            "Выберите товар", options=items, format_func=lambda i: f"{i['id']} — {i['name']}",
            key="delete_select",
        )
        if st.button("Удалить"):
            try:
                response = requests.delete(f"{BASE_URL}/items/{to_delete['id']}", timeout=TIMEOUT)
                if response.status_code == 200:
                    st.success("Товар удалён.")
                    st.rerun()
                else:
                    st.error(f"Не удалось удалить: {response.status_code}")
            except requests.exceptions.RequestException:
                st.error("Бэкенд недоступен.")
