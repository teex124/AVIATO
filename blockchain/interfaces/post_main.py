# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

class PostMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 875)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 875))
        
        
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
        
        # Эффект прозрачности
        MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        
        # Центральный виджет с эффектом размытия
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
        
        # Заголовок с неоновым эффектом
        self.label_2 = QtWidgets.QLabel("AVIATO ZENPAY", self.centralwidget)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setStyleSheet("""
            QLabel {
                font: bold 45px;
                color: #00aaff;
                text-transform: uppercase;
                letter-spacing: 2.5px;
                padding: 13px;
                border-bottom: 2.5px solid rgba(0, 170, 255, 0.5);
            }
        """)
        self.main_layout.addWidget(self.label_2)
        
        # Информация о балансе
        self.balance_layout = QtWidgets.QHBoxLayout()
        self.balance_layout.setSpacing(20)
        
        # Кошелек
        self.wallet_frame = QtWidgets.QFrame()
        self.wallet_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 35, 60, 0.7);
                border-radius: 19px;
                border: 1.25px solid rgba(0, 170, 255, 0.2);
                padding: 19px;
            }
        """)
        self.wallet_layout = QtWidgets.QVBoxLayout(self.wallet_frame)
        
        self.label = QtWidgets.QLabel("ВАШ КОШЕЛЕК", self.wallet_frame)
        self.label.setStyleSheet("font: bold 17.5px; color: #7fdbff;")
        self.wallet_address = QtWidgets.QLabel("0x000...000", self.wallet_frame)
        self.wallet_address.setStyleSheet("""
            QLabel {
                font: 22.5px 'Courier New';
                color: white;
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 10px;
                border: 1.25px solid rgba(0, 170, 255, 0.3);
            }
        """)
        self.wallet_layout.addWidget(self.label)
        self.wallet_layout.addWidget(self.wallet_address)
        self.balance_layout.addWidget(self.wallet_frame)
        
        # Баланс
        self.balance_frame = QtWidgets.QFrame()
        self.balance_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 35, 60, 0.7);
                border-radius: 19px;
                border: 1.25px solid rgba(0, 170, 255, 0.2);
                padding: 19px;
            }
        """)
        self.balance_inner_layout = QtWidgets.QVBoxLayout(self.balance_frame)
        
        self.label_3 = QtWidgets.QLabel("БАЛАНС", self.balance_frame)
        self.label_3.setStyleSheet("font: bold 17.5px; color: #7fdbff; border-radius: 20px; border: 2.5px solid #7fdbff; padding: 10px 0; background: rgba(0,170,255,0.07);")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.balance_inner_layout.addWidget(self.label_3)
        self.balance_value = QtWidgets.QLabel("0 RUB", self.balance_frame)
        self.balance_value.setStyleSheet("font: bold 30px; color: #00ffaa; background: rgba(0, 0, 0, 0.08); border-radius: 20px; border: 2.5px solid #00ffaa; padding: 10px 0;")
        self.balance_value.setAlignment(QtCore.Qt.AlignCenter)
        self.balance_inner_layout.addWidget(self.balance_value)
        self.balance_layout.addWidget(self.balance_frame)
        
        self.main_layout.addLayout(self.balance_layout)
        
        # Группа перевода средств
        self.transfer_group = QtWidgets.QGroupBox("ПЕРЕВОД СРЕДСТВ", self.centralwidget)
        self.transfer_group.setStyleSheet("""
            QGroupBox {
                font: bold 20px;
                color: #7fdbff;
                border: 2.5px solid rgba(0, 170, 255, 0.3);
                border-radius: 19px;
                margin-top: 25px;
                padding-top: 19px;
                background-color: rgba(30, 35, 60, 0.5);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 19px;
            }
        """)
        
        self.transfer_layout = QtWidgets.QGridLayout(self.transfer_group)
        self.transfer_layout.setVerticalSpacing(15)
        self.transfer_layout.setHorizontalSpacing(20)
        
        # Получатель
        self.label_7 = QtWidgets.QLabel("Кошелек получателя:", self.transfer_group)
        self.label_7.setStyleSheet("font: 17.5px; color: white;")
        self.lineEdit = QtWidgets.QLineEdit(self.transfer_group)
        self.lineEdit.setPlaceholderText("Введите адрес кошелька")
        self.lineEdit.setStyleSheet("""
            QLineEdit {
                font: 20px 'Courier New';
                color: white;
                background-color: rgba(0, 0, 0, 0.3);
                border: 1.25px solid rgba(0, 170, 255, 0.5);
                border-radius: 12.5px;
                padding: 15px;
                selection-background-color: rgba(0, 170, 255, 0.3);
            }
            QLineEdit:focus {
                border: 1.25px solid rgba(0, 170, 255, 0.8);
            }
        """)
        
        # Сумма
        self.label_8 = QtWidgets.QLabel("Сумма:", self.transfer_group)
        self.label_8.setStyleSheet("font: 17.5px; color: white;")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.transfer_group)
        self.lineEdit_2.setPlaceholderText("0.00 AVIATO COIN")
        self.lineEdit_2.setStyleSheet("""
            QLineEdit {
                font: bold 20px;
                color: white;
                background-color: rgba(0, 0, 0, 0.3);
                border: 1.25px solid rgba(0, 170, 255, 0.5);
                border-radius: 12.5px;
                padding: 15px;
                selection-background-color: rgba(0, 170, 255, 0.3);
            }
            QLineEdit:focus {
                border: 1.25px solid rgba(0, 170, 255, 0.8);
            }
        """)
        
        # Кнопка перевода
        self.pushButton_2 = QtWidgets.QPushButton("ОТПРАВИТЬ", self.transfer_group)
        self.pushButton_2.setStyleSheet("""
            QPushButton {
                font: bold 16px;
                color: white;
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00aaff, stop:1 #0088cc
                );
                border: none;
                border-radius: 15px;
                padding: 15px;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00bbff, stop:1 #0099ee
                );
            }
            QPushButton:pressed {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0088cc, stop:1 #0066aa
                );
            }
        """)
        self.pushButton_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        self.transfer_layout.addWidget(self.label_7, 0, 0)
        self.transfer_layout.addWidget(self.lineEdit, 0, 1)
        self.transfer_layout.addWidget(self.label_8, 1, 0)
        self.transfer_layout.addWidget(self.lineEdit_2, 1, 1)
        self.transfer_layout.addWidget(self.pushButton_2, 2, 0, 1, 2, alignment=QtCore.Qt.AlignCenter)
        
        self.main_layout.addWidget(self.transfer_group)
        
        # Разделитель
        self.separator = QtWidgets.QFrame()
        self.separator.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator.setStyleSheet("""
            QFrame {
                border: none;
                height: 1px;
                background-color: rgba(0, 170, 255, 0.2);
                margin: 15px 0;
            }
        """)
        self.main_layout.addWidget(self.separator)
        
        # Группа майнинга
        self.mining_group = QtWidgets.QGroupBox("МАЙНИНГ", self.centralwidget)
        self.mining_group.setStyleSheet("""
            QGroupBox {
                font: bold 20px;
                color: #7fdbff;
                border: 2.5px solid rgba(0, 170, 255, 0.3);
                border-radius: 19px;
                margin-top: 12.5px;
                padding-top: 19px;
                background-color: rgba(30, 35, 60, 0.5);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 19px;
            }
        """)
        
        self.mining_layout = QtWidgets.QVBoxLayout(self.mining_group)
        self.mining_layout.setSpacing(20)
        
        # Сложность
        self.difficulty_layout = QtWidgets.QHBoxLayout()
        self.label_4 = QtWidgets.QLabel("Сложность хэширования:")
        self.label_4.setStyleSheet("font: 17.5px; color: white; padding: 5px 0 0 0;")
        self.difficulty_value = QtWidgets.QLabel("0")
        self.difficulty_value.setStyleSheet("font: bold 16px; color: #ffaa00; padding: 5px 0 0 10px;")
        self.difficulty_layout.addWidget(self.label_4)
        self.difficulty_layout.addWidget(self.difficulty_value)
        self.difficulty_layout.addStretch()
        self.mining_layout.addLayout(self.difficulty_layout)

        # Добыто блоков
        self.blocks_layout = QtWidgets.QHBoxLayout()
        self.label_5 = QtWidgets.QLabel("Добыто блоков:")
        self.label_5.setStyleSheet("font: 17.5px; color: white; padding: 5px 0 0 0;")
        self.blocks_value = QtWidgets.QLabel("0")
        self.blocks_value.setStyleSheet("font: bold 16px; color: #00ffaa; padding: 5px 0 0 10px;")
        self.blocks_layout.addWidget(self.label_5)
        self.blocks_layout.addWidget(self.blocks_value)
        self.blocks_layout.addStretch()
        self.mining_layout.addLayout(self.blocks_layout)
        
        # Кнопка майнинга
        self.pushButton = QtWidgets.QPushButton("НАЧАТЬ МАЙНИНГ", self.mining_group)
        self.pushButton.setStyleSheet("""
            QPushButton {
                font: bold 16px;
                color: white;
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff5500, stop:1 #cc4400
                );
                border: none;
                border-radius: 15px;
                padding: 15px;
                min-width: 250px;
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
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.mining_layout.addWidget(self.pushButton, 0, QtCore.Qt.AlignCenter)
        
        self.main_layout.addWidget(self.mining_group)
        
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
        self.close_button.move(950, 10)
        self.close_button.clicked.connect(MainWindow.close)
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AVIATO ZENPAY"))
        self.label.setText(_translate("MainWindow", "ВАШ КОШЕЛЕК"))
        self.label_2.setText(_translate("MainWindow", "AVIATO ZENPAY"))
        self.label_3.setText(_translate("MainWindow", "БАЛАНС"))
        self.pushButton.setText(_translate("MainWindow", "НАЧАТЬ МАЙНИНГ"))
        self.label_4.setText(_translate("MainWindow", "Сложность хэширования:"))
        self.label_5.setText(_translate("MainWindow", "Добыто блоков:"))
        self.label_7.setText(_translate("MainWindow", "Кошелек получателя:"))
        self.label_8.setText(_translate("MainWindow", "Сумма:"))
        self.pushButton_2.setText(_translate("MainWindow", "ОТПРАВИТЬ"))

    def update_balance_rub(self, aviato_amount):
        try:
            aviato = float(aviato_amount)
        except Exception:
            aviato = 0.0
        rub = aviato * 250
        self.balance_value.setText(f"{rub:.2f} RUB")