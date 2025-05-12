import sys
import os
import pyodbc
import random

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer, QTime
from interfaces import pay
from blockchain.core.database import Database, UserRepository
from blockchain.services.wallet_service import WalletService
from blockchain.services.pilot_bot import PilotBot

class PaymentWindow(QMainWindow):
    def __init__(self, flight_data=None, parent=None):
        super().__init__(parent)
        self.ui = pay.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.flight_data = flight_data or {}
        self.time_left = 600
        
        self.wallet_service = WalletService()
        self.db = Database()
        self.user_repo = UserRepository(self.db)
        self.pilot_bot = PilotBot()
        
    
        self.pilot_chat_id = "6253156519"  
 
        self.initial_balance = self.get_wallet_balance()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        self.ui.pushButton.clicked.connect(self.confirm_payment)
        
        self.display_flight_info()
        self.start_timer()
    
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
    
    def start_timer(self):
        self.timer.start(1000) 
        self.update_timer()
    
    def update_timer(self):
        if self.time_left <= 0:
            self.timer.stop()
            self.ui.label_2.setText("00:00")
            QMessageBox.warning(self, "Время истекло", "Время на оплату истекло!")
            self.close()
            return
            
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.ui.label_2.setText(f"{minutes:02d}:{seconds:02d}")
        self.time_left -= 1
    
    def confirm_payment(self):
        try:
    
            initial_balance = self.wallet_service.get_balance("XJ2Y34MNFR")
            price = float(self.flight_data.get('price', 0))
            
     
            QTimer.singleShot(10000, lambda: self.verify_payment(initial_balance, price))
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при проверке оплаты: {str(e)}")
    
    def verify_payment(self, initial_balance, price):
        try:
            current_balance = self.wallet_service.get_balance("XJ2Y34MNFR")


            if current_balance > initial_balance:
                payment_data = {
                    'user_email': self.flight_data.get('user_email', ''),
                    'input_local_code': self.flight_data.get('input_local_code', ''),
                    'enter_local_code': self.flight_data.get('enter_local_code', ''),
                    'cost': price,
                    'exit_time': self.flight_data.get('exit_time', '')
                }
                
                try:
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
                    

                    if self.pilot_chat_id:
                        try:
                       
                            self.pilot_bot.send_flight_notification(self.pilot_chat_id, self.flight_data, send_photo=False)
                            print("Уведомление успешно отправлено в Telegram")
                        except Exception as e:
                            print(f"Ошибка при отправке уведомления в Telegram: {str(e)}")
                    else:
                        print("Pilot chat ID not found")
                    
                    QMessageBox.information(self, "Успех", "Оплата прошла успешно!")
                    self.timer.stop()
                    self.close()
                    
                except Exception as e:
                    print(f"Ошибка при сохранении данных: {str(e)}")
                    QMessageBox.warning(self, "Ошибка", f"Ошибка при сохранении данных: {str(e)}")
                finally:
                    if 'conn' in locals():
                        conn.close()
            else:
                # If balance hasn't increased, wait and try again
                print("Баланс не изменился, ожидание обновления...")
                QTimer.singleShot(5000, lambda: self.verify_payment(initial_balance, price))
                
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при проверке оплаты: {str(e)}")
    
    def check_payment(self):
        pass  
    
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()