import os
import random
from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QObject
from PyQt5.QtGui import QMovie
from interfaces import interface
import vlc
import interfaces.buy as buy


class AnimationManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = False
        self.movie = None
        self.timer = None
        self.splash_label = None
        self.media_player = None

    def start_animation(self, parent_window):
        if self._is_running:
            return False

        self._is_running = True
        

        self.splash_label = QLabel(parent_window)
        self.splash_label.setAttribute(Qt.WA_DeleteOnClose)
        self.splash_label.setAlignment(Qt.AlignCenter)
        self.splash_label.setGeometry(0, 0, parent_window.width(), parent_window.height())

        try:
            
            media_path = os.path.join(os.path.dirname(__file__), "resources", "music.mp3")
            if os.path.exists(media_path):
                self.media_player = vlc.MediaPlayer(media_path)
                self.media_player.play()
        except Exception as e:
            print(f"Error loading audio: {str(e)}")

        try:
            gif_path = os.path.join(os.path.dirname(__file__), "resources", "video.gif")
            if os.path.exists(gif_path):
                self.movie = QMovie(gif_path)
                self.movie.setCacheMode(QMovie.CacheAll)
                self.splash_label.setMovie(self.movie)
                
                self.movie.frameChanged.connect(self._check_last_frame)
                self.movie.finished.connect(self._cleanup)
                
                self.movie.start()
                self.splash_label.show()
                return True
            else:
                print(f"Animation file not found at: {gif_path}")
                self._cleanup()
                return False
        except Exception as e:
            print(f"Error loading animation: {str(e)}")
            self._cleanup()
            return False

    def _check_last_frame(self, frame_number):
        if self.movie and frame_number == self.movie.frameCount() - 1:
            self._cleanup()

    def _cleanup(self):
        if not self._is_running:
            return

        if self.movie:
            self.movie.stop()
            self.movie.deleteLater()
            self.movie = None

        if self.splash_label:
            self.splash_label.hide()
            self.splash_label.deleteLater()
            self.splash_label = None

        if self.media_player:
            self.media_player.stop()
            self.media_player.release()
            self.media_player = None

        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()
            self.timer = None

        self._is_running = False


class Funces(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = interface.Ui_MainWindow()
        self.ui.setupUi(self)
        self.global_atribut = None
        self.buy_window = None
        self.animation_manager = AnimationManager(self)

    def anim_frame(self):
        target_frame = self.ui.frame
        original_geom = target_frame.geometry()
    
        scale_factor = 1.05
        new_width = int(original_geom.width() * scale_factor)
        new_height = int(original_geom.height() * scale_factor)
        new_x = original_geom.x() - (new_width - original_geom.width()) // 2
        new_y = original_geom.y() - (new_height - original_geom.height()) // 2
        
        larger_geom = QRect(new_x, new_y, new_width, new_height)
        
        animation = QPropertyAnimation(target_frame, b"geometry")
        animation.setDuration(300)
        animation.setKeyValueAt(0, original_geom)
        animation.setKeyValueAt(0.7, larger_geom)  
        animation.setKeyValueAt(1, original_geom) 
        animation.setEasingCurve(QEasingCurve.OutBack) 
        animation.start()

    def show_window_enter(self, atribut='full_reg_frst'):
        self.anim_frame()
        
        if atribut == 'full_reg_frst':
            self.ui.lineEdit.setText('')
            self.ui.label.setText('Создать учетную запись')
            self.ui.lineEdit.setPlaceholderText('test@gmail.com')
            self.ui.label_3.setText('Введите почту:')
            self.global_atribut = atribut

        elif atribut == 'full_reg_second':
            self.ui.lineEdit.setText('')
            self.ui.label.setText('Создать учетную запись')
            self.ui.label_3.setText('Введите пароль:')
            self.ui.lineEdit.setPlaceholderText('password123')
            self.global_atribut = atribut

        elif atribut == 'email_accesses':
            self.ui.lineEdit.setText('')
            self.ui.label.setText('Создать учетную запись')
            self.ui.label_3.setText('Введите код с письма на почте:')
            self.ui.lineEdit.setPlaceholderText('123452')
            self.global_atribut = atribut
            
        elif atribut == 'enter_frst':
            self.ui.lineEdit.setText('')
            self.ui.label.setText('Войти в учетную запись')
            self.ui.label_3.setText('Введите почту:')
            self.ui.lineEdit.setPlaceholderText('test@gmail.com')
            self.global_atribut = atribut

        elif atribut == 'enter_second':
            self.ui.lineEdit.setText('')
            self.ui.label.setText('Войти в учетную запись')
            self.ui.label_3.setText('Введите пароль:')
            self.ui.lineEdit.setPlaceholderText('password123')
            self.global_atribut = atribut
        
        elif atribut == 'main':
            import main_window
            self.buy_window = main_window.MainInterface()
            if hasattr(self, 'log_email'):
                self.buy_window.log_email = self.log_email
            self.buy_window.show()
            self.close()

    def anim_start(self):
        self.animation_manager.start_animation(self)

    def resizeEvent(self, event):
        if hasattr(self, 'animation_manager') and self.animation_manager.splash_label:
            self.animation_manager.splash_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def closeEvent(self, event):
        if hasattr(self, 'animation_manager'):
            self.animation_manager._cleanup()
        super().closeEvent(event)