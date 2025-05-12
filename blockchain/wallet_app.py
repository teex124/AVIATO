import os
import json
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from interfaces import wallet
from interfaces.post_main import PostMainWindow
from blockchain.core.database import Database, UserRepository
from blockchain.services.wallet_service import WalletService

class WalletApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = wallet.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.db = Database()
        self.user_repo = UserRepository(self.db)
        self.wallet_service = WalletService()
        
        self.current_wallet = None
        self.setup_connections()
        
    def setup_connections(self):
        self.ui.pushButton.clicked.connect(self.check_balance)
        self.ui.pushButton_2.clicked.connect(self.transfer_coins)
        
    def set_wallet(self, wallet_address):
        self.current_wallet = wallet_address
        self.ui.label_3.setText(f"Кошелек: {wallet_address}")
        self.check_balance()
        
    def check_balance(self):
        if not self.current_wallet:
            QMessageBox.warning(self, "Ошибка", "Кошелек не установлен")
            return
            
        try:
            balance = self.wallet_service.get_balance(self.current_wallet)
            self.ui.label_4.setText(f"Баланс: {balance} AVIATO COIN")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при проверке баланса: {str(e)}")
            
    def transfer_coins(self):
        if not self.current_wallet:
            QMessageBox.warning(self, "Ошибка", "Кошелек не установлен")
            return
            
        recipient = self.ui.lineEdit.text()
        amount = float(self.ui.lineEdit_2.text())
        
        if not recipient or not amount:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
            
        try:
            self.wallet_service.transfer_coins(self.current_wallet, recipient, amount)
            QMessageBox.information(self, "Успех", "Перевод выполнен успешно")
            self.check_balance()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при переводе: {str(e)}")
            
    def closeEvent(self, event):
        if self.db:
            self.db.close()
        event.accept()

def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = WalletApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

