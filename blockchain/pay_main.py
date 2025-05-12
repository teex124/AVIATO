import os
import json
import datetime
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from interfaces import pay
from blockchain.core.database import Database, UserRepository
from blockchain.services.wallet_service import WalletService

class PaymentMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = pay.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.db = Database()
        self.user_repo = UserRepository(self.db)
        self.wallet_service = WalletService()
        
        self.setup_connections()
        
    def setup_connections(self):
        self.ui.pushButton.clicked.connect(self.process_payment)
        
    def process_payment(self):
        email = self.ui.lineEdit.text()
        amount = float(self.ui.lineEdit_2.text())
        
        if not email or not amount:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
            
        user = self.user_repo.get_user_by_email(email)
        
        if not user:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден")
            return
            
        wallet_address = user[3]
        current_balance = self.wallet_service.get_balance(wallet_address)
        
        if current_balance < amount:
            QMessageBox.warning(self, "Ошибка", "Недостаточно средств")
            return
            
        try:
            self.wallet_service.transfer_coins(wallet_address, "XJ2Y34MNFR", amount)
            self.user_repo.update_balance(email, current_balance - amount)
            QMessageBox.information(self, "Успех", "Оплата прошла успешно")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при оплате: {str(e)}")
            
    def closeEvent(self, event):
        if self.db:
            self.db.close()
        event.accept()                                                                               