import json
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


def report_to_file(filename: Optional[str] = None):
    """
    Декоратор для сохранения результата функции-отчёта в файл.

    Аргументы:
        filename (str, optional): имя файла для сохранения.
                                  Если не указано, генерируется автоматически.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if isinstance(result, pd.DataFrame):
                data = result.to_dict(orient="records")
            else:
                data = result

            if filename:
                file_path = f"reports/{filename}.json"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"reports/{func.__name__}_{timestamp}.json"

            os.makedirs("reports", exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            return result

        return wrapper

    return decorator


@report_to_file()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: str
) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние 3 месяца от указанной даты.

    Аргументы:
        transactions (pd.DataFrame): датафрейм с транзакциями
        category (str): название категории
        date (str): дата в формате "DD.MM.YYYY", от которой считаем 3 месяца

    Возвращает:
        pd.DataFrame: отфильтрованный датафрейм
    """
    # Проверяем, что датафрейм не пустой
    if transactions.empty:
        return pd.DataFrame()

    # Парсим дату из строки
    try:
        end_date = datetime.strptime(date, "%d.%m.%Y")
    except ValueError:
        return pd.DataFrame()

    # Вычисляем дату 3 месяца назад
    start_date = end_date - timedelta(days=90)

    # Копируем датафрейм и парсим даты
    df = transactions.copy()

    def parse_date(date_str):
        if isinstance(date_str, str) and "." in date_str:
            try:
                return datetime.strptime(date_str.split()[0], "%d.%m.%Y")
            except:
                return None
        return None

    df["Дата_парс"] = df["Дата операции"].apply(parse_date)

    # Фильтруем
    filtered = df[
        (df["Категория"] == category)
        & (df["Дата_парс"] >= start_date)
        & (df["Дата_парс"] <= end_date)
        & (df["Сумма операции"] < 0)
        & (df["Статус"] == "OK")
    ]

    # Удаляем вспомогательную колонку
    filtered = filtered.drop(columns=["Дата_парс"])

    return filtered


@report_to_file("spending_summary")
def spending_summary(transactions: pd.DataFrame, category: str, date: str) -> dict:
    """
    Возвращает сводку по тратам по категории.

    Аргументы:
        transactions (pd.DataFrame): датафрейм с транзакциями
        category (str): название категории
        date (str): дата в формате "DD.MM.YYYY"

    Возвращает:
        dict: сводка с общей суммой и количеством транзакций
    """
    filtered = spending_by_category(transactions, category, date)

    if filtered.empty:
        return {
            "category": category,
            "period": f"3 месяца до {date}",
            "total_spent": 0,
            "transaction_count": 0,
        }

    total_spent = abs(filtered["Сумма операции"].sum())
    transaction_count = len(filtered)

    return {
        "category": category,
        "period": f"3 месяца до {date}",
        "total_spent": round(total_spent, 2),
        "transaction_count": transaction_count,
        "transactions": filtered[
            ["Дата операции", "Описание", "Сумма операции"]
        ].to_dict(orient="records"),
    }


@report_to_file()
def spending_by_category_monthly(
    transactions: pd.DataFrame, category: str, date: str
) -> dict:
    """
    Возвращает ежемесячные траты по категории.

    Аргументы:
        transactions (pd.DataFrame): датафрейм с транзакциями
        category (str): название категории
        date (str): дата в формате "DD.MM.YYYY"

    Возвращает:
        dict: разбивка трат по месяцам
    """
    filtered = spending_by_category(transactions, category, date)

    if filtered.empty:
        return {
            "category": category,
            "period": f"3 месяца до {date}",
            "monthly_spending": [],
        }

    # Добавляем колонку с месяцем
    df = filtered.copy()
    df["Месяц"] = df["Дата операции"].apply(
        lambda x: (
            x.split()[0][3:5] + "." + x.split()[0][6:10]
            if isinstance(x, str) and len(x) > 0
            else ""
        )
    )

    monthly = df.groupby("Месяц")["Сумма операции"].sum().abs().round(2)

    return {
        "category": category,
        "period": f"3 месяца до {date}",
        "monthly_spending": [
            {"month": month, "spent": amount}
            for month, amount in sorted(monthly.items())
        ],
    }
