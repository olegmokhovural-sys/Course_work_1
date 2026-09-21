import datetime

import pandas as pd
import requests

from utils import get_transactions_from_excel

ALPHA_VANTAGE_KEY = "1M74RV6J63N0LZ3D"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"


def get_greeting():
    """Возвращает приветствие в зависимости от времени суток."""
    hour = datetime.datetime.now().hour
    if 0 <= hour < 6:
        return "Доброй ночи"
    elif 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 24:
        return "Добрый вечер"
    return "Здравствуйте"


def get_exchange_rate(currency):
    """Получает курс валюты к рублю."""
    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": currency,
        "to_currency": "RUB",
        "apikey": ALPHA_VANTAGE_KEY,
    }
    try:
        response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=10)
        data = response.json()
        rate = data.get("Realtime Currency Exchange Rate", {}).get("5. Exchange Rate")
        return float(rate) if rate else 0
    except:
        return 0


def get_stock_price(symbol):
    """Получает текущую цену акции."""
    params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": ALPHA_VANTAGE_KEY}
    try:
        response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=10)
        data = response.json()
        price = data.get("Global Quote", {}).get("05. price")
        return float(price) if price else 0
    except:
        return 0


def get_transactions_data():
    """Получает и обрабатывает транзакции."""
    transactions = get_transactions_from_excel()
    df = pd.DataFrame(transactions)

    # Оставляем только успешные операции
    df = df[df["Статус"] == "OK"]

    # Расходы (отрицательные суммы)
    expenses = df[df["Сумма операции"] < 0]
    expenses["Сумма"] = abs(expenses["Сумма операции"])

    # Доходы (положительные суммы)
    income = df[df["Сумма операции"] > 0]
    income["Сумма"] = income["Сумма операции"]

    return expenses, income


def get_expenses_data(expenses):
    """Обрабатывает расходы."""
    # Группируем расходы по категориям
    expenses_by_category = (
        expenses.groupby("Категория")["Сумма"].sum().round(0).astype(int)
    )

    # Список категорий для основных расходов (исключаем Переводы и Наличные)
    exclude_categories = ["Переводы", "Наличные"]

    main_expenses = []
    transfers_and_cash = []

    for category, amount in expenses_by_category.items():
        if category in exclude_categories:
            transfers_and_cash.append({"category": category, "amount": amount})
        else:
            main_expenses.append({"category": category, "amount": amount})

    # Сортируем по убыванию суммы
    main_expenses.sort(key=lambda x: x["amount"], reverse=True)

    return {
        "total_amount": int(expenses["Сумма"].sum()),
        "main": main_expenses,
        "transfers_and_cash": transfers_and_cash,
    }


def get_income_data(income):
    """Обрабатывает доходы."""
    # Группируем доходы по категориям
    income_by_category = income.groupby("Категория")["Сумма"].sum().round(0).astype(int)

    income_list = []
    for category, amount in income_by_category.items():
        income_list.append({"category": category, "amount": amount})

    # Сортируем по убыванию суммы
    income_list.sort(key=lambda x: x["amount"], reverse=True)

    return {"total_amount": int(income["Сумма"].sum()), "main": income_list}


def get_currency_rates():
    """Получает курсы валют."""
    currencies = ["USD", "EUR"]
    rates = []
    for currency in currencies:
        rate = get_exchange_rate(currency)
        if rate:
            rates.append({"currency": currency, "rate": round(rate, 2)})
    return rates


def get_stock_prices():
    """Получает цены акций."""
    stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    prices = []
    for stock in stocks:
        price = get_stock_price(stock)
        if price:
            prices.append({"stock": stock, "price": round(price, 2)})
    return prices


def get_full_report():
    """Формирует полный отчёт."""
    # Получаем данные о транзакциях
    expenses, income = get_transactions_data()

    return {
        "expenses": get_expenses_data(expenses),
        "income": get_income_data(income),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }
