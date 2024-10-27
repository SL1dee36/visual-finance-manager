# ui.py
from customtkinter import *
import json
from . import visualisation, finance
import requests

class App(CTk):
    def __init__(self):
        super().__init__()
        self.title("VisualFin beta")
        self.geometry("800x600")
        self.minsize(320,600)
        self.data = self.load_data()  # load_data now sets self.balance, income, expenses

        self.currency = "USD"

        self.currencies = ["USD", "EUR", "RUB", "KZT", "GBP", "JPY", "CNY"]
        self.exchange_rates = self.get_exchange_rates()

        self.load_frame()
        self.load_stats_widgets()
        self.load_finance_widgets()
        self.update_transaction_history()
        self.update_balance_and_ie()  # Обновляем баланс и I/E при запуске
        self.update_balance_label()


    def load_data(self):
        try:
            with open("src/data/database.json", "r") as f:
                data = json.load(f)  # Загружаем данные в локальную переменную data

                transactions = data.get("transactions", [])
                if transactions:
                    self.balance = sum(t['amount'] for t in transactions if t['type'] == "Доход") - sum(abs(t['amount']) for t in transactions if t['type'] == "Расход")
                    self.income = sum(t['amount'] for t in transactions if t['type'] == "Доход")
                    self.expenses = sum(abs(t['amount']) for t in transactions if t['type'] == "Расход")
                else:
                    self.balance = 0
                    self.income = 0
                    self.expenses = 0
                    self.currency = "USD"

                self.data = data # Присваиваем self.data ПОСЛЕ вычисления баланса
                return self.data


        except (FileNotFoundError, json.JSONDecodeError):
            initial_data = {"transactions": []}
            with open("src/data/database.json", "w") as f:
                json.dump(initial_data, f, indent=4)
            self.data = initial_data
            self.balance = 0
            self.income = 0
            self.expenses = 0
            self.currency = "USD"
            return self.data

    def save_data(self):
        with open("src/data/database.json", "w") as f:
            json.dump(self.data, f, indent=4)

    def get_exchange_rates(self):
        url = "https://api.exchangerate-api.com/v4/latest/USD" #  Базовая валюта USD
        try:
            response = requests.get(url)
            response.raise_for_status() #  Проверяем на ошибки
            data = response.json()
            rates = data['rates']
            return rates
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения курсов валют: {e}")
            return {} #  Возвращаем пустой словарь в случае ошибки

    def convert_currency(self, new_currency):
        if new_currency == self.currency:
            return
        if new_currency in self.exchange_rates and self.currency in self.exchange_rates :
            new_balance = self.balance * self.exchange_rates[new_currency] / self.exchange_rates[self.currency] # Конвертация через USD
        elif new_currency in self.exchange_rates:
            new_balance = self.balance / self.exchange_rates[self.currency] * self.exchange_rates[new_currency]
        elif self.currency in self.exchange_rates:
            new_balance = self.balance * self.exchange_rates[new_currency]
        else:
            print("Невозможно конвертировать валюту. Курсы не доступны.")
            return
        
        self.balance = new_balance
        self.currency = new_currency
        self.update_balance_label()

    def update_balance_label(self):
            formatted_balance = "{:.2f}".format(self.balance)
            # Изменяем текст СУЩЕСТВУЮЩЕЙ метки
            self.current_balance.configure(text=f"Balance: {formatted_balance} {self.currency}")
            self.income_to_expenses.configure(text=self.calculate_income_to_expenses_ratio())
 
    def load_frame(self):
        self.main_frame = CTkFrame(self, corner_radius=5)
        self.main_frame.pack(padx=5, pady=5, fill=BOTH, expand=True)

        self.stats_widget = CTkFrame(self.main_frame, height=50)
        self.stats_widget.pack(padx=5, pady=5, fill=X)

        self.finance_frame = CTkFrame(self.main_frame)
        self.finance_frame.pack(padx=5, pady=5, fill=BOTH, expand=True)

    def load_stats_widgets(self):

        # Создаем метку баланса ТОЛЬКО ОДИН РАЗ
        self.current_balance = CTkLabel(self.stats_widget, text="")  # Изначально пустой текст
        self.current_balance.pack(side=LEFT, padx=5, pady=5)

        try: # Обработка деления на ноль
            income_to_expenses_ratio = self.income / self.expenses if self.expenses != 0 else float('inf')  #  inf, если expenses = 0
            income_to_expenses_text = f"I/E ≈ {income_to_expenses_ratio:.2f}" # Округление до 2 знаков

            if income_to_expenses_ratio == float('inf'):
                income_to_expenses_text = "I/E ≈ ∞" # Отображаем бесконечность
            elif self.income == 0 and self.expenses == 0:
                income_to_expenses_text = "I/E ≈ N/A" #  N/A, если и income и expenses равны 0


        except ZeroDivisionError: # Перехватываем исключение, если expenses = 0
                income_to_expenses_text = "I/E ≈ N/A"

        self.income_to_expenses = CTkLabel(self.stats_widget, text=income_to_expenses_text)
        self.income_to_expenses.pack(side=LEFT, padx=5, pady=5)

        self.select_currency = CTkOptionMenu(self.stats_widget,
                                            values=self.currencies,
                                            command=self.convert_currency,
                                            width=60)
        self.select_currency.set(self.currency)
        self.select_currency.pack(side=LEFT, padx=5, pady=5)

        self.update_balance_label() #  Вызов после создания виджетов

        # Функция для проверки ширины экрана и изменения размещения виджетов
        def check_screen_width(event=None):
            if self.winfo_width() < 400:
                self.current_balance.pack_configure(side=TOP)
                self.income_to_expenses.pack_configure(side=TOP)
                self.income_to_expenses.configure(text=income_to_expenses_text)
                self.select_currency.pack_configure(side=TOP)
            else:
                self.current_balance.pack_configure(side=LEFT)
                self.income_to_expenses.pack_configure(side=LEFT)
                self.income_to_expenses.configure(text=income_to_expenses_text)
                self.select_currency.pack_configure(side=LEFT)

        # Вызываем функцию при запуске и при изменении размера окна
        check_screen_width()
        self.bind("<Configure>", check_screen_width)

        self.update_balance_label()  # Обновляем текст метки после создания

    def calculate_income_to_expenses_ratio(self):
        try:
            income_to_expenses_ratio = self.income / self.expenses if self.expenses != 0 else float('inf')
            ratio_text = f"I/E ≈ {income_to_expenses_ratio:.2f}"

            if income_to_expenses_ratio == float('inf'):
                ratio_text = "I/E ≈ ∞"
            elif self.income == 0 and self.expenses == 0:
                ratio_text = "I/E ≈ N/A"

        except ZeroDivisionError:
            ratio_text = "I/E ≈ N/A"

        return ratio_text

    def update_balance_and_ie(self):
        self.update_balance_label()
        self.income_to_expenses.configure(text=self.calculate_income_to_expenses_ratio())

    def load_finance_widgets(self):

        fin_utils = CTkFrame(self.finance_frame)
        fin_utils.pack(side=TOP,padx=5, pady=5, fill=X)
       
        add_income_button = CTkButton(fin_utils, text="Добавить доходы", command=self.show_add_income_dialog)
        add_income_button.pack(padx=5,pady=5,side=LEFT)

        add_expense_button = CTkButton(fin_utils, text="Внести расходы", command=self.show_add_expense_dialog)
        add_expense_button.pack(padx=5,pady=5,side=LEFT)

        # self.transaction_history = []
        self.history_frame = CTkFrame(self.finance_frame)
        self.history_frame.pack(pady=(10,5), fill=BOTH, expand=True,padx=5)

    def show_add_income_dialog(self):
        dialog = finance.AddIncomeDialog(self)
        if dialog.result is not None:
            amount, currency, date, description = dialog.result
            finance.add_income(self, amount, currency, date, description)

    def show_add_expense_dialog(self):
        dialog = finance.AddExpenseDialog(self)
        if dialog.result is not None:
            amount, currency, date, description = dialog.result
            finance.add_expense(self, amount, currency, date, description)


    def update_transaction_history(self):
        for child in self.history_frame.winfo_children():
            child.destroy()

        for i, transaction in enumerate(self.data.get("transactions", [])):
            bg_color = "gray" if i % 2 == 0 else "#404040"

            row_frame = CTkFrame(self.history_frame, fg_color=bg_color)
            row_frame.pack(fill=X, pady=(5,0),padx=5)

            date_label = CTkLabel(row_frame, text=transaction["date"])
            date_label.pack(side=LEFT, padx=5)

            type_label = CTkLabel(row_frame, text=transaction["type"])
            type_label.pack(side=LEFT, padx=5)

            description_label = CTkLabel(row_frame, text=transaction["description"])
            description_label.pack(side=LEFT, padx=5)

            amount_label = CTkLabel(row_frame, text=f"{transaction['amount']:.2f} {transaction['currency']}")
            amount_label.pack(side=LEFT, padx=5)

            edit_button = CTkButton(row_frame, text="⁝", command=lambda i=i: self.edit_transaction(i), width=30, hover_color="#2e4053", fg_color="#5d6d7e",text_color="#d6eaf8",font=("Times",24))
            edit_button.pack(side=RIGHT, padx=5,pady=5)

    def edit_transaction(self, index):
        #  Здесь будет код для редактирования транзакции (пока заглушка)
        print(f"Редактирование транзакции {index}")
        # ... (добавьте функционал для редактирования)