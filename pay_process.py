from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer, QTime
from interfaces import pay

class PaymentWindow(QMainWindow):
    def __init__(self, flight_data=None, parent=None):
        super().__init__(parent)
        self.ui = pay.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.flight_data = flight_data or {}
        self.time_left = 600  
        
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        self.ui.pushButton.clicked.connect(self.confirm_payment)
        
        self.display_flight_info()
        self.start_timer()
    
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
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            "Вы уверены, что совершили перевод?", 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Успех", "Оплата подтверждена! Рейс забронирован.")
            self.timer.stop()
            self.close()
    
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()