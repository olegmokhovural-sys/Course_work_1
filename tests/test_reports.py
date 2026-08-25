import pandas as pd
from src.reports import spending_by_category


def test_spending_by_category():
    """Тест функции трат по категории."""
    data = {
        "Дата операции": [
            "01.12.2021 10:00:00",
            "15.12.2021 14:00:00",
            "01.11.2021 10:00:00",
            "01.09.2021 10:00:00"
        ],
        "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты", "Супермаркеты"],
        "Сумма операции": [-100, -50, -200, -300],
        "Статус": ["OK", "OK", "OK", "OK"]
    }
    df = pd.DataFrame(data)

    result = spending_by_category(df, "Супермаркеты", "31.12.2021")

    assert len(result) == 3