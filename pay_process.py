import sys
import os
import pyodbc
import threading
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer, QTime
from interfaces import pay
from blockchain.core.database import Database, UserRepository
from blockchain.services.wallet_service import WalletService
from blockchain.services.pilot_bot import PilotBot
from utilits.mail import send_receipt_email
from blockchain.services import pilot_bot
from multiprocessing import Process


class PaymentWindow(QMainWindow):
    def __init__(self, flight_data=None, parent=None):
        super().__init__(parent)
        self.ui = pay.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.flight_data = flight_data or {}
        

        self.wallet_service = WalletService()
        self.db = Database()
        self.user_repo = UserRepository(self.db)
        

        self.bot_thread = None



        self.initial_balance = self.get_wallet_balance()
        
        self.ui.pushButton.clicked.connect(self.confirm_payment)
        
        self.display_flight_info()
    
   
    def get_wallet_balance(self) -> float:
        """Get current wallet balance"""
        return self.wallet_service.get_balance("XJ2Y34MNFR")
    
    def display_flight_info(self):
        if not self.flight_data:
            self.ui.flight_info.setPlainText("Информация о полете недоступна")
            return
            
        info_text = (
            f"Вылет: {self.flight_data.get('departure', 'N/A')}\n"
            f"Прилет: {self.flight_data.get('arrival', 'N/A')}\n"
            f"Время вылета: {self.flight_data.get('time', 'N/A')}\n"
            f"Стоимость: {self.flight_data.get('price', 'N/A')} AVIATO COIN\n"
        )
        self.ui.plainTextEdit.setPlainText(info_text)
    
    def confirm_payment(self):
        try:
            current_balance = self.get_wallet_balance()
            price = float(self.flight_data.get('price', 0))
            
            print(f"\n=== Проверка оплаты ===")
            print(f"Начальный баланс: {self.initial_balance}")
            print(f"Текущий баланс: {current_balance}")
            print(f"Требуемая сумма: {price}")
            print(f"Разница: {current_balance - self.initial_balance}")
            print("======================\n")
            
            # Проверяем, увеличился ли баланс на сумму платежа (с допуском +/- 10)
            if current_balance >= self.initial_balance + price - 10:
                self.process_successful_payment(price)
            else:
                QMessageBox.warning(self, "Ошибка", 
                                  "Платеж не обнаружен. Пожалуйста, убедитесь, что вы отправили средства.")
                
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при проверке оплаты: {str(e)}")
    
    def process_successful_payment(self, price):
        """Process all actions after successful payment"""
        payment_data = {
            'user_email': self.flight_data.get('user_email', ''),
            'input_local_code': self.flight_data.get('input_local_code', ''),
            'enter_local_code': self.flight_data.get('enter_local_code', ''),
            'cost': price,
            'exit_time': self.flight_data.get('exit_time', '')
        }
        

        conn = pyodbc.connect(
            "Driver={SQL Server};"
            "Server=KOMPUTER;"
            "Database=AVIATO_DB;"
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO pays (user_email, input_local_code, enter_local_code, cost, exit_time)
            VALUES (?, ?, ?, ?, ?)
        """, (
            payment_data['user_email'],
            payment_data['input_local_code'],
            payment_data['enter_local_code'],
            payment_data['cost'],
            payment_data['exit_time']
        ))
        
        conn.commit()
        print("Данные успешно сохранены в базу данных")
        

        if payment_data.get('user_email'):
            try:
                send_receipt_email(payment_data['user_email'], payment_data)
                print(f"Чек успешно отправлен на {payment_data['user_email']}")
            except Exception as e:
                print(f"Ошибка при отправке чека по email: {str(e)}")
        
        print(payment_data)
        
        try:
            wallet_service = WalletService()
            bot = PilotBot(wallet_service)
            bot.bot_iter(payment_data)
            
            QMessageBox.information(self, "Успех", "Оплата прошла успешно!")
        except Exception as e:
            print(f"Ошибка при работе с ботом: {str(e)}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка при работе с ботом: {str(e)}")
        if 'conn' in locals():
            conn.close()
