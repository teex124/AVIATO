# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 700)
        MainWindow.setMinimumSize(QtCore.QSize(800, 700))
        
        MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Основная палитра
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(20, 25, 45))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(30, 35, 60))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(40, 45, 80))
        palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(40, 45, 80))
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(0, 170, 255))
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        MainWindow.setPalette(palette)
        
        # Центральный виджет
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 20, 40, 0.9);
                border-radius: 20px;
                border: 1px solid rgba(0, 170, 255, 0.3);
            }
        """)
        
        # Главный layout
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)
        
        # Заголовок
        self.label_title = QtWidgets.QLabel("AVIATO ZENPAY", self.centralwidget)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setStyleSheet("""
            QLabel {
                font: bold 45px;
                color: #00aaff;
                text-transform: uppercase;
                letter-spacing: 2.5px;
                padding: 13px;
                border-bottom: 2.5px solid rgba(0, 170, 255, 0.5);
            }
        """)
        self.main_layout.addWidget(self.label_title)
        
        # Табы
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setStyleSheet("""
    QTabWidget {
        background: transparent;
        border: none;
    }
    QTabBar {
        spacing: 5px;
    }
    QTabBar::tab {
        background: rgba(30, 35, 60, 0.7);
        color: #b2bec3;
        padding: 8px 15px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        border: 1px solid rgba(0, 170, 255, 0.3);
        border-bottom: none;
        font-size: 13px;
        font-weight: bold;
        min-width: 80px;
    }
    QTabBar::tab:selected {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00aaff, stop:1 #0088cc);
        color: white;
        border: 1px solid rgba(0, 170, 255, 0.5);
    }
    QTabWidget::pane {
        border: 1px solid rgba(0, 170, 255, 0.3);
        border-top: none;
        border-radius: 0 8px 8px 8px;
        background: rgba(30, 35, 60, 0.5);
        padding: 15px;
    }
""")
        
        # Вкладка входа
        self.tab_login = QtWidgets.QWidget()
        self.tab_login.setObjectName("tab_login")
        
        self.login_layout = QtWidgets.QVBoxLayout(self.tab_login)
        self.login_layout.setContentsMargins(20, 20, 20, 20)
        self.login_layout.setSpacing(20)
        
        # Поле для введенных пользователем слов
        self.label_user_words = QtWidgets.QLabel("Введенные слова:", self.tab_login)
        self.label_user_words.setStyleSheet("font: bold 16px; color: #7fdbff;")
        self.login_layout.addWidget(self.label_user_words)
        
        self.plainTextEdit_2 = QtWidgets.QTextEdit(self.tab_login)
        self.plainTextEdit_2.setStyleSheet("""
            QTextEdit {
                font: 16px 'Courier New';
                color: white;
                background-color: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(0, 170, 255, 0.5);
                border-radius: 10px;
                padding: 15px;
                min-height: 100px;
            }
        """)
        self.plainTextEdit_2.setReadOnly(True)
        self.login_layout.addWidget(self.plainTextEdit_2)
        
        # Поле ввода слова
        self.word_input_layout = QtWidgets.QHBoxLayout()
        
        self.lineEdit = QtWidgets.QLineEdit(self.tab_login)
        self.lineEdit.setPlaceholderText("Введите следующее слово...")
        self.lineEdit.setStyleSheet("""
            QLineEdit {
                font: 16px;
                color: white;
                background-color: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(0, 170, 255, 0.5);
                border-radius: 10px;
                padding: 15px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 170, 255, 0.8);
            }
        """)
        self.word_input_layout.addWidget(self.lineEdit)
        
        self.pushButton_2 = QtWidgets.QPushButton("Добавить", self.tab_login)
        self.pushButton_2.setStyleSheet("""
            QPushButton {
                font: bold 14px;
                color: white;
                background-color: rgba(0, 170, 255, 0.7);
                border: none;
                border-radius: 10px;
                padding: 15px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: rgba(0, 170, 255, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(0, 140, 225, 0.7);
            }
        """)
        self.word_input_layout.addWidget(self.pushButton_2)
        
        self.pushButton_4 = QtWidgets.QPushButton("Убрать", self.tab_login)
        self.pushButton_4.setStyleSheet("""
            QPushButton {
                font: bold 14px;
                color: white;
                background-color: rgba(255, 85, 85, 0.7);
                border: none;
                border-radius: 10px;
                padding: 15px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: rgba(255, 85, 85, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(225, 65, 65, 0.7);
            }
        """)
        self.word_input_layout.addWidget(self.pushButton_4)
        
        self.login_layout.addLayout(self.word_input_layout)
        
        # Кнопка входа
        self.pushButton_3 = QtWidgets.QPushButton("ВОЙТИ В КОШЕЛЕК", self.tab_login)
        self.pushButton_3.setStyleSheet("""
            QPushButton {
                font: bold 16px;
                color: white;
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00aa00, stop:1 #008800
                );
                border: none;
                border-radius: 10px;
                padding: 15px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00bb00, stop:1 #009900
                );
            }
            QPushButton:pressed {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #008800, stop:1 #006600
                );
            }
        """)
        self.login_layout.addWidget(self.pushButton_3, 0, QtCore.Qt.AlignCenter)
        
        self.tabWidget.addTab(self.tab_login, "Вход")
        
        # Вкладка регистрации
        self.tab_register = QtWidgets.QWidget()
        self.tab_register.setObjectName("tab_register")
        
        self.register_layout = QtWidgets.QVBoxLayout(self.tab_register)
        self.register_layout.setContentsMargins(20, 20, 20, 20)
        self.register_layout.setSpacing(20)
        
        # Поле для новой мнемонической фразы
        self.label_new_words = QtWidgets.QLabel("Ваша новая секретная фраза:", self.tab_register)
        self.label_new_words.setStyleSheet("font: bold 16px; color: #7fdbff;")
        self.register_layout.addWidget(self.label_new_words)
        
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.tab_register)
        self.plainTextEdit.setStyleSheet("""
            QPlainTextEdit {
                font: 16px 'Courier New';
                color: white;
                background-color: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(0, 170, 255, 0.5);
                border-radius: 10px;
                padding: 15px;
                min-height: 150px;
            }
        """)
        self.plainTextEdit.setReadOnly(True)
        self.register_layout.addWidget(self.plainTextEdit)
        
        # Предупреждение
        self.warning_label = QtWidgets.QLabel("Сохраните эту фразу в безопасном месте! Без нее вы не сможете восстановить доступ к кошельку.", self.tab_register)
        self.warning_label.setStyleSheet("""
            QLabel {
                font: 14px;
                color: #ff5555;
                background-color: rgba(255, 85, 85, 0.1);
                border: 1px solid rgba(255, 85, 85, 0.3);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        self.warning_label.setWordWrap(True)
        self.register_layout.addWidget(self.warning_label)
        
        # Кнопка создания
        self.pushButton = QtWidgets.QPushButton("СОЗДАТЬ КОШЕЛЕК", self.tab_register)
        self.pushButton.setStyleSheet("""
            QPushButton {
                font: bold 16px;
                color: white;
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff5500, stop:1 #cc4400
                );
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6600, stop:1 #dd5500
                );
            }
            QPushButton:pressed {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #cc4400, stop:1 #aa3300
                );
            }
        """)
        self.register_layout.addWidget(self.pushButton)
        
        self.tabWidget.addTab(self.tab_register, "Регистрация")
        
        self.main_layout.addWidget(self.tabWidget)
        
        # Кнопка закрытия
        self.close_button = QtWidgets.QPushButton("✕", self.centralwidget)
        self.close_button.setStyleSheet("""
            QPushButton {
                font: bold 16px;
                color: white;
                background-color: transparent;
                border: none;
                padding: 7px 14px;
                qproperty-alignment: AlignCenter;
            }
            QPushButton:hover {
                color: #ff5555;
            }
        """)
        self.close_button.setFixedSize(50, 50)
        self.close_button.move(750, 10)
        # Подключение обработчика нажатия на кнопку закрытия
        self.close_button.clicked.connect(MainWindow.close)
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AVIATO ZENPAY - Вход"))
        self.label_title.setText(_translate("MainWindow", "AVIATO ZENPAY"))
        self.label_user_words.setText(_translate("MainWindow", "Введенные слова:"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Введите следующее слово..."))
        self.pushButton_2.setText(_translate("MainWindow", "Добавить"))
        self.pushButton_4.setText(_translate("MainWindow", "Убрать"))
        self.pushButton_3.setText(_translate("MainWindow", "ВОЙТИ В КОШЕЛЕК"))
        self.label_new_words.setText(_translate("MainWindow", "Ваша новая секретная фраза:"))
        self.warning_label.setText(_translate("MainWindow", "Сохраните эту фразу в безопасном месте! Без нее вы не сможете восстановить доступ к кошельку."))
        self.pushButton.setText(_translate("MainWindow", "СОЗДАТЬ КОШЕЛЕК"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_login), _translate("MainWindow", "Вход"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_register), _translate("MainWindow", "Регистрация"))