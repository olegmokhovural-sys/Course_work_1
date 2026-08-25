import pandas as pd
import json
from views import get_full_report
from utils import get_transactions_from_excel
from services import get_cashback_analysis
from utils import get_transactions_from_excel
from reports import spending_by_category, spending_summary, spending_by_category_monthly


def format_report(report):
    expenses = report["expenses"]
    expenses_data = {
        "total_amount": expenses["total_amount"],
        "main": expenses["main"],
        "transfers_and_cash": expenses["transfers_and_cash"]
    }

    income = report["income"]
    income_data = {
        "total_amount": income["total_amount"],
        "main": income["main"]
    }

    currency_rates = []
    for rate in report["currency_rates"]:
        currency_rates.append({
            "currency": rate["currency"],
            "rate": rate["rate"]
        })

    stock_prices = []
    for stock in report["stock_prices"]:
        stock_prices.append({
            "stock": stock["stock"],
            "price": stock["price"]
        })

    return {
        "expenses": expenses_data,
        "income": income_data,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }


if __name__ == "__main__":
    try:
        raw_report = get_full_report()

        formatted_report = format_report(raw_report)

        print(json.dumps(formatted_report, ensure_ascii=False, indent=2))

        print("\n" + "=" * 50)
        print("СТАТИСТИКА ЗА ПЕРИОД")
        print("=" * 50)
        print(f"Всего расходов: {formatted_report['expenses']['total_amount']} руб.")
        print(f"Всего доходов: {formatted_report['income']['total_amount']} руб.")
        print(
            f"Баланс: {formatted_report['income']['total_amount'] - formatted_report['expenses']['total_amount']} руб.")
        print("=" * 50)

        # Вывод топ-5 расходов по категориям
        print("\nТОП-5 РАСХОДОВ ПО КАТЕГОРИЯМ:")
        print("-" * 30)
        for i, item in enumerate(formatted_report['expenses']['main'][:5], 1):
            print(f"{i}. {item['category']}: {item['amount']} руб.")

        # Вывод курсов валют
        print("\nКУРСЫ ВАЛЮТ:")
        print("-" * 30)
        for rate in formatted_report['currency_rates']:
            print(f"1 {rate['currency']} = {rate['rate']} RUB")

        # Вывод цен акций
        print("\nЦЕНЫ АКЦИЙ S&P 500:")
        print("-" * 30)
        for stock in formatted_report['stock_prices']:
            print(f"{stock['stock']}: ${stock['price']}")

    except FileNotFoundError:
        print("Ошибка: файл data/operations.xlsx не найден!")
    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")

if __name__ == "__main__":
    transactions = get_transactions_from_excel()

    result = get_cashback_analysis(transactions, 2021, 12)

    print("=" * 60)
    print("АНАЛИЗ КЕШБЭКА ЗА ДЕКАБРЬ 2021")
    print("=" * 60)
    print(result)

if __name__ == "__main__":
    transactions_list = get_transactions_from_excel()
    df = pd.DataFrame(transactions_list)

    print("=" * 60)
    print("ОТЧЁТЫ ПО КАТЕГОРИЯМ (из данных Excel)")
    print("=" * 60)

    date = "31.12.2021"
    category = "Супермаркеты"

    # Транзакции по категории за 3 месяца
    result = spending_by_category(df, category, date)
    print(f"\n1. Транзакции по категории '{category}' за 3 месяца до {date}:")
    print(f"   Найдено транзакций: {len(result)}")
    if not result.empty:
        print(result[["Дата операции", "Описание", "Сумма операции"]].head())

    # Сводка по категории
    summary = spending_summary(df, category, date)
    print(f"\n2. Сводка по категории '{category}':")
    print(f"   Период: {summary['period']}")
    print(f"   Всего потрачено: {summary['total_spent']} руб.")
    print(f"   Количество транзакций: {summary['transaction_count']}")

    # Ежемесячные траты
    monthly = spending_by_category_monthly(df, category, date)
    print(f"\n3. Ежемесячные траты по категории '{category}':")
    for item in monthly["monthly_spending"]:
        print(f"   {item['month']}: {item['spent']} руб.")