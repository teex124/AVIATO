import sys
import os
import pyodbc
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from interfaces import enter
from blockchain.core.database import Database, UserRepository
from blockchain.services.wallet_service import WalletService

class EnterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = enter.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.db = Database()
        self.user_repo = UserRepository(self.db)
        self.wallet_service = WalletService()
        
        self.setup_connections()
        
    def setup_connections(self):
        self.ui.pushButton.clicked.connect(self.login)
        self.ui.pushButton_2.clicked.connect(self.register)
        
    def login(self):
        email = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
            
        user = self.user_repo.get_user_by_email(email)
        
        if user and user[2] == password:
            QMessageBox.information(self, "Успех", "Вход выполнен успешно")
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный email или пароль")
            
    def register(self):
        email = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
            
        if self.user_repo.get_user_by_email(email):
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким email уже существует")
            return
            
        wallet_address = self.wallet_service.create_wallet(email)
        
        if self.user_repo.create_user(email, password, wallet_address):
            QMessageBox.information(self, "Успех", "Регистрация успешна")
        else:
            QMessageBox.warning(self, "Ошибка", "Ошибка при регистрации")
            
    def closeEvent(self, event):
        if self.db:
            self.db.close()
        event.accept()