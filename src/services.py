import json
from datetime import datetime


def analyze_cashback(transactions, year, month):
    """
    Анализирует, сколько кешбэка можно получить по категориям за месяц.

    Аргументы:
        transactions (list): список транзакций из Excel
        year (int): год для анализа
        month (int): месяц для анализа

    Возвращает:
        str: JSON-строка с результатами
    """
    # Шаг 1: Фильтруем транзакции по году и месяцу
    filtered = []
    for t in transactions:
        date_str = t.get("Дата операции", "")
        if date_str:
            try:
                # Парсим дату "31.12.2021 16:44:00"
                date_parts = date_str.split()[0].split(".")
                t_year = int(date_parts[2])
                t_month = int(date_parts[1])
                if t_year == year and t_month == month:
                    filtered.append(t)
            except:
                pass

    # Шаг 2: Оставляем только расходы (отрицательные суммы) со статусом OK
    expenses = []
    for t in filtered:
        amount = t.get("Сумма операции", 0)
        status = t.get("Статус", "")
        if amount < 0 and status == "OK":
            expenses.append(t)

    # Шаг 3: Группируем расходы по категориям
    categories = {}
    for t in expenses:
        category = t.get("Категория", "Без категории")
        amount = abs(t.get("Сумма операции", 0))
        if category in categories:
            categories[category] += amount
        else:
            categories[category] = amount

    # Шаг 4: Считаем кешбэк для каждой категории
    result_categories = []
    for category, spent in categories.items():
        cashback = int(spent // 100)  # 1 рубль за каждые 100 рублей
        result_categories.append({
            "category": category,
            "spent": round(spent, 2),
            "cashback": cashback
        })

    # Шаг 5: Сортируем по убыванию кешбэка
    result_categories.sort(key=lambda x: x["cashback"], reverse=True)

    # Шаг 6: Формируем результат
    result = {
        "year": year,
        "month": month,
        "total_spent": sum(c["spent"] for c in result_categories),
        "categories": result_categories
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


def get_cashback_analysis(transactions, year, month):
    """Основная функция для вызова."""
    return analyze_cashback(transactions, year, month)