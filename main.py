import sys
import datetime, json, threading, hashlib
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
import utilits.mail as mail
import low_lvl_func
from qt_func_enter import Funces
import subprocess
import os

class MainWindow(Funces):
    def __init__(self):
        super().__init__()
        self.anim_start()
        self.logs = False
        self.is_login_mode = None 
        self.log_email = None

        self.iter_enter()
        self.email = None
        self.cod = None
        self.conn = None
        self.password = None 

        self.log_password = None

        self.ui.pushButton.clicked.connect(self.toggle_login_register)
        

        if hasattr(self.ui, 'pushButton_wallet'):
            self.ui.pushButton_wallet.clicked.connect(self.open_wallet)

    def toggle_login_register(self):
        if self.is_login_mode:
            self.show_window_enter(atribut='full_reg_frst')
            self.ui.pushButton.setText("У меня уже есть аккаунт")
        else:
            self.show_window_enter(atribut='enter_frst')
            self.ui.pushButton.setText("У меня еще нет аккаунта")
        
        self.is_login_mode = not self.is_login_mode

    def logger(self, status):
        employee_data = {'date': str(datetime.datetime.now().date()),
                         'status': status}
        with open("data.json", "w") as file:
            json.dump(employee_data, file)
    
    def log_read(self):
        try:
            with open("data.json", "r") as file:
               
                return json.load(file)  
        except:
            return None

    def iter_enter(self):
        if self.log_read() is None:
            print(self.log_read())
            self.logs = False
        else:
            date = datetime.datetime(int(self.log_read()['date'].split('-')[0]),
                                     int(self.log_read()['date'].split('-')[1]),
                                     int(self.log_read()['date'].split('-')[2]))
            status = self.log_read()['status']
            date_razn = (datetime.datetime.now().timestamp() - date.timestamp())/(60*60*24)
            
            self.logs = True
        
        print(self.logs)
        if self.logs == False:
            self.is_login_mode = False
            self.show_window_enter(atribut='full_reg_frst')
            self.ui.pushButton.setText("У меня уже есть аккаунт")
            
            self.enter_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
            self.enter_shortcut.activated.connect(self.handle_next_step)        
            self.ui.pushButton_2.clicked.connect(self.handle_next_step)

        elif self.logs == True:
            self.is_login_mode = True
            self.show_window_enter(atribut='enter_frst')
            self.ui.pushButton.setText("У меня еще нет аккаунта")
            
            self.enter_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
            self.enter_shortcut.activated.connect(self.handle_next_step)
            self.ui.pushButton_2.clicked.connect(self.handle_next_step)

    def handle_next_step(self):
        current = self.global_atribut
        if current == 'full_reg_frst' and len(self.ui.lineEdit.text()) > 0:
            self.email = self.ui.lineEdit.text()
            

            if self.email_exists_in_db(self.email):
                QMessageBox.warning(self, "Ошибка", "Аккаунт с такой почтой уже существует!")
                self.is_login_mode = True
                self.show_window_enter(atribut='enter_frst')
                self.ui.pushButton.setText("У меня еще нет аккаунта")
                return
                
            self.show_window_enter(atribut='full_reg_second')

        elif current == 'full_reg_second' and len(self.ui.lineEdit.text()) > 0:
            import random 
            self.code = str(random.randint(100000, 999999))
            self.autoswap_thread = threading.Thread(target=lambda: mail.send_confirmation_email(self.email, self.code), daemon=True)
            self.autoswap_thread.start()
            self.password = hashlib.sha256((self.ui.lineEdit.text()).encode()).hexdigest()
            self.show_window_enter(atribut='email_accesses')

        elif current == 'email_accesses' and len(self.ui.lineEdit.text()) > 0:
            if self.ui.lineEdit.text() == self.code:
                self.logger('Standart')
                low_lvl_func.insert_data('users', (self.email, self.password), "user_mail, user_password")
                self.log_email = self.email
                self.show_window_enter(atribut='main')

        elif current == 'enter_frst':
            self.log_email = self.ui.lineEdit.text()
            self.show_window_enter(atribut='enter_second')
        elif current == 'enter_second':
            self.log_password = self.ui.lineEdit.text()
            print(self.db_search())
            if self.db_search():
                self.show_window_enter(atribut='main')

    def email_exists_in_db(self, email):
        for i in low_lvl_func.read_data('users'):
            if i[0] == email:
                return True
        return False

    def db_search(self):
        for i in low_lvl_func.read_data('users'):
            if i[0] == self.log_email and i[1] == hashlib.sha256(self.log_password.encode()).hexdigest():
                return True
            else: 
                ...
        return False    

    def open_wallet(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            wallet_path = os.path.join(current_dir, 'blockchain', 'pay_main.py')
            subprocess.Popen([sys.executable, wallet_path])
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть кошелек: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()   
    sys.exit(app.exec_())