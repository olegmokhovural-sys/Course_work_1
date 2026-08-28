import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.views import (
    get_greeting,
    get_exchange_rate,
    get_stock_price,
    get_transactions_data,
    get_expenses_data,
    get_income_data,
    get_currency_rates,
    get_stock_prices,
    get_full_report,
)


def test_get_greeting():
    """Тест: функция возвращает строку."""
    result = get_greeting()
    assert isinstance(result, str)
    assert result in [
        "Доброй ночи",
        "Доброе утро",
        "Добрый день",
        "Добрый вечер",
        "Здравствуйте",
    ]


@patch("views.requests.get")
def test_get_exchange_rate(mock_get):
    """Тест: получение курса валюты."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Realtime Currency Exchange Rate": {"5. Exchange Rate": "91.23"}
    }
    mock_get.return_value = mock_response

    rate = get_exchange_rate("USD")
    assert rate == 91.23


def test_get_expenses_data():
    """Тест: группировка расходов."""
    data = {"Категория": ["Супермаркеты", "Топливо"], "Сумма": [100, 200]}
    expenses = pd.DataFrame(data)

    result = get_expenses_data(expenses)

    assert result["total_amount"] == 300
    assert len(result["main"]) == 2


def test_get_income_data():
    """Тест: группировка доходов."""
    data = {"Категория": ["Пополнения", "Бонусы"], "Сумма": [1000, 100]}
    income = pd.DataFrame(data)

    result = get_income_data(income)

    assert result["total_amount"] == 1100
    assert len(result["main"]) == 2


@patch("views.get_stock_price")
def test_get_stock_prices(mock_get):
    """Тест: получение цен акций."""
    mock_get.side_effect = [150.12, 3173.18, 2742.39, 296.71, 1007.08]

    prices = get_stock_prices()

    assert len(prices) == 5
    assert prices[0]["stock"] == "AAPL"
    assert prices[0]["price"] == 150.12
