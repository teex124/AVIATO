import sys
import os
import pyodbc
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from interfaces import main
from blockchain.core.database import Database, UserRepository
from blockchain.services.wallet_service import WalletService
from pay_process import PaymentWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = main.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.db = Database()
        self.user_repo = UserRepository(self.db)
        self.wallet_service = WalletService()
        
        self.current_user = None
        self.selected_doping = None
        self.photo_path = None
        
        self.setup_connections()
        self.load_doping_options()
        
    def setup_connections(self):
        self.ui.pushButton.clicked.connect(self.login)
        self.ui.pushButton_2.clicked.connect(self.register)
        self.ui.pushButton_3.clicked.connect(self.book_flight)
        self.ui.pushButton_4.clicked.connect(self.select_photo)
        self.ui.comboBox.currentIndexChanged.connect(self.doping_selected)
        
    def load_doping_options(self):
        try:
            conn = pyodbc.connect(
                "Driver={SQL Server};"
                "Server=KOMPUTER;"
                "Database=AVIATO_DB;"
            )
            cursor = conn.cursor()
            
            cursor.execute("SELECT DopingID, Name, Price FROM doping")
            doping_options = cursor.fetchall()
            
            self.ui.comboBox.clear()
            self.ui.comboBox.addItem("Выбор параметра")
            
            for doping in doping_options:
                self.ui.comboBox.addItem(f"{doping[1]} - {doping[2]} AVIATO COIN", doping[0])
                
        except Exception as e:
            print(f"Error loading doping options: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
                
    def doping_selected(self, index):
        if index > 0:
            self.selected_doping = self.ui.comboBox.currentData()
        else:
            self.selected_doping = None
            
    def select_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите фото",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_name:
            self.photo_path = file_name
            pixmap = QPixmap(file_name)
            scaled_pixmap = pixmap.scaled(
                self.ui.label_5.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.ui.label_5.setPixmap(scaled_pixmap)
            
    def login(self):
        email = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
            
        user = self.user_repo.get_user_by_email(email)
        
        if user and user[2] == password:
            self.current_user = user
            self.ui.stackedWidget.setCurrentIndex(1)
            self.ui.label_3.setText(f"Добро пожаловать, {user[1]}!")
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
            
    def book_flight(self):
        if not self.current_user:
            QMessageBox.warning(self, "Ошибка", "Войдите в систему")
            return
            
        departure = self.ui.lineEdit_3.text()
        arrival = self.ui.lineEdit_4.text()
        time = self.ui.timeEdit.time().toString("HH:mm")
        
        if not departure or not arrival:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
            
        try:
            conn = pyodbc.connect(
                "Driver={SQL Server};"
                "Server=KOMPUTER;"
                "Database=AVIATO_DB;"
            )
            cursor = conn.cursor()
            
            if self.selected_doping:
                cursor.execute("SELECT Price FROM doping WHERE DopingID = ?", (self.selected_doping,))
                doping_price = cursor.fetchone()[0]
            else:
                doping_price = 0
                
            base_price = 1000
            total_price = base_price + doping_price
            
            flight_data = {
                'user_email': self.current_user[1],
                'departure': departure,
                'arrival': arrival,
                'time': time,
                'price': total_price,
                'photo_path': self.photo_path,
                'input_local_code': departure,
                'enter_local_code': arrival,
                'exit_time': time,
                'doping_id': self.selected_doping
            }
            
            payment_window = PaymentWindow(flight_data, self)
            payment_window.show()
            
        except Exception as e:
            print(f"Error booking flight: {str(e)}")
            QMessageBox.warning(self, "Ошибка", "Ошибка при бронировании полета")
        finally:
            if 'conn' in locals():
                conn.close()
                
    def closeEvent(self, event):
        if self.db:
            self.db.close()
        event.accept()