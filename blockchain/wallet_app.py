from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from interfaces.post_main import PostMainWindow
from services.wallet_service import WalletService


class WalletApp(QMainWindow):
    def __init__(self, wallet_service):  # Add parameter here
        super().__init__()
        self.ui = PostMainWindow()
        self.ui.setupUi(self)
        
        self.wallet_service = wallet_service  # Store the passed service
        
        self.setup_wallet_ui()
        self.connect_signals()

    def setup_wallet_ui(self):
        """Setup wallet UI elements"""
        self.setWindowTitle("AVIATO ZENPAY")
        self.update_difficulty_display()
        self.update_mined_blocks_display()
        self.ui.label.setText("Ваш кошелек: ")
        self.ui.lineEdit.clear()
        self.ui.lineEdit_2.clear()

    def update_difficulty_display(self):
        """Update mining difficulty display"""
        difficulty = self.wallet_service.hash_repo.get_current_difficulty()
        self.ui.difficulty_value.setText(str(difficulty))

    def update_mined_blocks_display(self):
        """Update mined blocks display"""
        difficulty = self.wallet_service.hash_repo.get_current_difficulty()
        mined_blocks = difficulty - 1
        self.ui.blocks_value.setText(str(mined_blocks))

    def connect_signals(self):
        """Connect UI signals to handlers"""
        self.ui.pushButton.clicked.connect(self.handle_mining)
        self.ui.pushButton_2.clicked.connect(self.handle_transfer)

    def set_wallet(self, wallet: str):
        """Set wallet address and update UI"""
        self.wallet = wallet
        self.ui.label.setText(f"Ваш кошелек: {wallet}")
        self.update_balance()

    def update_balance(self):
        """Update wallet balance display"""
        balance = self.wallet_service.get_balance(self.wallet)
        self.ui.label_3.setText(f"Баланс: {balance:.2f} AVIATO COIN")
        self.update_balance_rub(balance)

    def update_balance_rub(self, aviato_amount):
        try:
            aviato = float(aviato_amount)
        except Exception:
            aviato = 0.0
        rub = aviato * 250
        self.ui.balance_value.setText(f"{rub:.2f} RUB")

    def handle_mining(self):
        """Handle mining button click"""
        if self.wallet_service.mine_block(self.wallet):
            QMessageBox.information(
                self,
                'Успешно',
                'Блок успешно намайнен!',
                QMessageBox.Ok
            )
            self.update_balance()
            self.update_difficulty_display()
            self.update_mined_blocks_display()

   
        else:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Не удалось намайнить блок',
                QMessageBox.Ok
            )

    def handle_transfer(self):
        """Handle transfer button click"""
        recipient = self.ui.lineEdit.text()
        try:
            amount = float(self.ui.lineEdit_2.text())
        except ValueError:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Введите корректную сумму',
                QMessageBox.Ok
            )
            return

        if not recipient:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Введите адрес получателя',
                QMessageBox.Ok
            )
            return

        if self.wallet_service.transfer_coins(self.wallet, recipient, amount):
            QMessageBox.information(
                self,
                'Успешно',
                f'Перевод {amount:.2f} AVIATO на кошелек {recipient} выполнен',
                QMessageBox.Ok
            )
            self.update_balance()
            self.ui.lineEdit.clear()
            self.ui.lineEdit_2.clear()

            # Send Telegram notification after transfer
         
        else:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Не удалось выполнить перевод',
                QMessageBox.Ok
            )

  

def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = WalletApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
