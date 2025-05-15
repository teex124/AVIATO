import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from interfaces.interface import Ui_MainWindow
from services.wallet_service import WalletService
from core.database import Database, WordRepository
from wallet_app import WalletApp

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
      
        self.wallet_service = WalletService()
        self.db = Database()
        self.word_repo = WordRepository(self.db)
        
 
        self.words = []
        self.words_index = []
        self.registration_words = []
        self.user_words = []
        self.wallet_window = None
   
        self.setup_ui()
        self.connect_signals()
        self.generate_words()

    def setup_ui(self):
  
        self.setWindowTitle("AVIATO: ZENPAY")
        self.ui.plainTextEdit.clear()
        self.ui.plainTextEdit_2.clear()
        self.ui.lineEdit.clear()

    def connect_signals(self):
    
        self.ui.pushButton.clicked.connect(self.handle_registration)
        self.ui.pushButton_2.clicked.connect(lambda: self.add_word(True))
        self.ui.pushButton_4.clicked.connect(lambda: self.add_word(False))
        self.ui.pushButton_3.clicked.connect(self.handle_login)

    def generate_words(self):
        """Generate new registration words"""
        self.words = []
        self.words_index = []
        self.registration_words = []
        self.ui.plainTextEdit.clear()
        
        for _ in range(5):
            word_data = self.word_repo.get_random_word()
            if word_data:
                word_id, word = word_data
                self.words.append((word_id, word))
                self.registration_words.append(word)
                self.words_index.append(word_id)
                self.ui.plainTextEdit.appendPlainText(word)

    def add_word(self, add: bool):

        if add:
            self.user_words.append(self.ui.lineEdit.text())
        else:
            self.user_words.pop()
        self.ui.plainTextEdit_2.setPlainText(' '.join(self.user_words))

    def handle_registration(self):
     
        reply = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы точно сохранили эти слова? После подтверждения будет создан аккаунт.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            wallet = self.wallet_service.create_account(self.words_index)
            if wallet:
                QMessageBox.information(
                    self,
                    'Успешно',
                    f'Аккаунт успешно создан!\nВаш кошелек: {wallet}',
                    QMessageBox.Ok
                )
                self.generate_words()
            else:
                QMessageBox.warning(
                    self,
                    'Ошибка',
                    'Не удалось создать аккаунт',
                    QMessageBox.Ok
                )

    def handle_login(self):
  
        entered_words = self.ui.plainTextEdit_2.toPlainText().split()
        
        if not entered_words:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Пожалуйста, введите слова для входа',
                QMessageBox.Ok
            )
            return

        if len(entered_words) != 5:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Пожалуйста, введите ровно 5 слов',
                QMessageBox.Ok
            )
            return

        wallet = self.wallet_service.verify_login(entered_words)
        if wallet:
            QMessageBox.information(
                self,
                'Успешно',
                f'Вход выполнен успешно!\nВаш кошелек: {wallet}',
                QMessageBox.Ok
            )
            self.open_wallet_window(wallet)
        else:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Неверные слова для входа',
                QMessageBox.Ok
            )

    def open_wallet_window(self, wallet: str):
        self.hide()
        self.wallet_window = WalletApp(self.wallet_service)  # Pass the service
        self.wallet_window.set_wallet(wallet)
        self.wallet_window.show()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()                                                                               