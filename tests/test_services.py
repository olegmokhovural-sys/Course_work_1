import json
from src.services import analyze_cashback


def test_analyze_cashback():
    transactions = [
        {
            "Дата операции": "01.12.2021 10:00:00",
            "Категория": "Супермаркеты",
            "Сумма операции": -150,
            "Статус": "OK",
        },
        {
            "Дата операции": "15.12.2021 14:00:00",
            "Категория": "Супермаркеты",
            "Сумма операции": -50,
            "Статус": "OK",
        },
        {
            "Дата операции": "01.11.2021 10:00:00",
            "Категория": "Супермаркеты",
            "Сумма операции": -100,
            "Статус": "OK",
        },
    ]

    result = analyze_cashback(transactions, 2021, 12)
    data = json.loads(result)

    assert data["total_spent"] == 200
    assert data["categories"][0]["cashback"] == 2
