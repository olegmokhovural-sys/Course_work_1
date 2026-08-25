import pandas as pd


def get_transactions_from_excel():
    """
    Считывает финансовые операции из Excel и возвращает список словарей.
    """
    transactions_excel = pd.read_excel("data/operations.xlsx")
    transactions_list = transactions_excel.to_dict(orient="records")
    return transactions_list


if __name__ == "__main__":
    transactions = get_transactions_from_excel()

    print(f"Количество транзакций: {len(transactions)}")
    print("Первые 5 транзакций:")
    print(transactions[:5])