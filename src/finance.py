# finance.py
import requests
from datetime import datetime
from customtkinter import CTkToplevel, CTkLabel, CTkEntry, CTkOptionMenu, CTkButton

def fin_add_income(app, amount, currency, date, description):
    converted_amount = convert_to_base_currency(app, amount, currency, date)
    if converted_amount is None:
        print(f"Ошибка конвертации валюты для дохода: {amount} {currency} на {date}")
        return

    app.income += converted_amount
    app.balance += converted_amount
    add_transaction(app, date, "Доход", description, converted_amount, "USD")
    app.save_data()  # Сохраняем данные *перед* обновлением интерфейса
    app.update_balance_and_ie()
    app.update_transaction_history()


def fin_add_expense(app, amount, currency, date, description):
    converted_amount = convert_to_base_currency(app, amount, currency, date)
    if converted_amount is None:
        print(f"Ошибка конвертации валюты для расхода: {amount} {currency} на {date}")
        return

    app.expenses += converted_amount
    app.balance -= converted_amount
    add_transaction(app, date, "Расход", description, -converted_amount, "USD")
    app.save_data() # Сохраняем данные *перед* обновлением интерфейса
    app.update_balance_and_ie()
    app.update_transaction_history()


def add_transaction(app, date, type, description, amount, currency="USD"):
    transaction = {
        "date": date,
        "type": type,
        "description": description,
        "amount": amount,
        "currency": currency
    }
    app.data["transactions"].append(transaction)

def convert_to_base_currency(app, amount, currency, date):
    if currency == app.currency:
        return amount
    try:
        rate = get_exchange_rate(currency, app.currency, date)
        if rate is None:
            print(f"Не удалось получить курс обмена для {currency} на {date}")
            return None  # Вернуть None в случае ошибки
        return amount * rate
    except Exception as e:
        print(f"Ошибка при конвертации валюты: {e}")
        return None


def get_exchange_rate(from_currency, to_currency, date_str):
    date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
    timestamp = int(date_obj.timestamp())
    url = f"https://api.exchangerate.host/{timestamp}"
    params = {
        'base': from_currency,
        'symbols': to_currency
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data['rates'][to_currency]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка API: {e}")
        return None
    except KeyError as e:
        print(f"Ошибка данных API: {e}")
        return None



class AddIncomeDialog(CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Добавить доход")
        self.geometry("300x200")
        self.resizable(False, False)

        self.result = None
        self.parent = parent

        self.create_widgets()

    def create_widgets(self):
        print(0)
        amount_label = CTkLabel(self, text="Сумма:")
        amount_label.grid(row=0, column=0, padx=5, pady=5, sticky="w") # sticky="w" для выравнивания по левому краю

        self.amount_entry = CTkEntry(self)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        currency_label = CTkLabel(self, text="Валюта:")
        currency_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.currency_option = CTkOptionMenu(self, values=self.parent.currencies)
        self.currency_option.set(self.parent.currency)
        self.currency_option.grid(row=1, column=1, padx=5, pady=5)

        date_label = CTkLabel(self, text="Дата (дд.мм.гггг):")
        date_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.date_entry = CTkEntry(self)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        description_label = CTkLabel(self, text="За что:")
        description_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.description_entry = CTkEntry(self)
        self.description_entry.grid(row=3, column=1, padx=5, pady=5)

        add_button = CTkButton(self, text="Добавить", command=self.add_income)
        add_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

    def add_income(self):
        print(1)
        try:
            amount = float(self.amount_entry.get())
            currency = self.currency_option.get()
            date = self.date_entry.get()
            description = self.description_entry.get()

            # Проверка формата даты
            try:
                datetime.strptime(date, "%d.%m.%Y")
            except ValueError:
                print("Неверный формат даты. Используйте дд.мм.гггг")
                return

            self.parent.result = (amount, currency, date, description) # Присваиваем результат непосредственно в app
            self.destroy()
            # Добавляем вызов add_income из finance.py здесь
            fin_add_income(self.parent, amount, currency, date, description)
        except ValueError:
            print("Введите числовое значение для суммы.")
        print(2)

class AddExpenseDialog(CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Добавить расход") #  Изменено название
        self.geometry("300x200")
        self.resizable(False, False)

        self.result = None
        self.parent = parent

        self.create_widgets()

    def create_widgets(self):
        amount_label = CTkLabel(self, text="Сумма:")
        amount_label.grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = CTkEntry(self)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        currency_label = CTkLabel(self, text="Валюта:")
        currency_label.grid(row=1, column=0, padx=5, pady=5)
        self.currency_option = CTkOptionMenu(self, values=self.parent.currencies)
        self.currency_option.set(self.parent.currency)
        self.currency_option.grid(row=1, column=1, padx=5, pady=5)

        date_label = CTkLabel(self, text="Дата (дд.мм.гггг):")
        date_label.grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = CTkEntry(self)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        description_label = CTkLabel(self, text="На что:")  # Изменена метка
        description_label.grid(row=3, column=0, padx=5, pady=5)
        self.description_entry = CTkEntry(self)
        self.description_entry.grid(row=3, column=1, padx=5, pady=5)

        add_button = CTkButton(self, text="Добавить", command=self.add_expense)
        add_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            currency = self.currency_option.get()
            date = self.date_entry.get()
            description = self.description_entry.get()
            self.parent.result = (amount, currency, date, description) # Присваиваем результат непосредственно в app
            self.destroy()
            # Добавляем вызов add_expense из finance.py здесь
            fin_add_expense(self.parent, amount, currency, date, description)
        except ValueError:
            print("Введите числовое значение для суммы.")