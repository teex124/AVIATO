import requests
from PyQt5.QtWidgets import QMainWindow, QComboBox, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QByteArray, Qt, QDateTime
from interfaces import buy
import pyodbc, time
from collections import defaultdict
import math
import datetime
import pay_process
import random 

class MainInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = buy.Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.airport_data = []
        self.country_city_map = defaultdict(list)
        self.city_airport_map = defaultdict(list)
        self.current_departure_airport = None
        self.current_arrival_airport = None
        self.cost = 0 
        self.money = 0.01
        self.current_zoom = 5  
        self.distance_km = 0
        self.cash = 0 
        self.doping_data = {} 
        self.log_email = None  
        

        current_time = QDateTime.currentDateTime().addSecs(10 * 3600)
        self.ui.dateTimeEdit.setDateTime(current_time)
        self.ui.dateTimeEdit.setMinimumDateTime(QDateTime.currentDateTime())
        self.ui.dateTimeEdit.dateTimeChanged.connect(self.calculate_price_based_on_time)
        
        self.setup_combo_boxes()
        
        self.ui.comboBox.currentIndexChanged.connect(self.update_cities_combo)
        self.ui.comboBox_2.currentIndexChanged.connect(self.update_departure_airports_combo)
        self.ui.comboBox_3.currentIndexChanged.connect(self.update_selected_departure_airport)
        
        self.ui.comboBox_4.currentIndexChanged.connect(self.update_arrival_cities_combo)
        self.ui.comboBox_5.currentIndexChanged.connect(self.update_arrival_airports_combo)
        self.ui.comboBox_6.currentIndexChanged.connect(self.update_selected_arrival_airport)
        
        self.ui.pushButton_2.clicked.connect(self.zoom_in)
        self.ui.pushButton_3.clicked.connect(self.zoom_out)
        
        self.ui.spinBox.valueChanged.connect(self.update)
        self.ui.pushButton.clicked.connect(self.book_flight)

        self.load_doping_data()
        self.load_initial_map()
    
    def calculate_price_based_on_time(self):
        if not self.current_departure_airport or not self.current_arrival_airport:
            return
            

        selected_time = self.ui.dateTimeEdit.dateTime()
        current_time = QDateTime.currentDateTime()
        
        hours_diff = current_time.secsTo(selected_time) / 3600
        
        time_factor = max(0.5, min(2.0, 1.5 - (hours_diff / 48)))
        

        self.money = self.distance_km * time_factor
        self.update()
    
    def book_flight(self):
        if not self.current_departure_airport:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите аэропорт вылета!")
            return
            
        if not self.current_arrival_airport:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите аэропорт прилета!")
            return
            
        if self.current_departure_airport['code'] == self.current_arrival_airport['code']:
            QMessageBox.warning(self, "Ошибка", "Аэропорты вылета и прилета не могут совпадать!")
            return
            
        selected_time = self.ui.dateTimeEdit.dateTime()
        current_time = QDateTime.currentDateTime()
        
        if selected_time <= current_time.addSecs(36000): 
            QMessageBox.warning(self, "Ошибка", "Время вылета должно быть как минимум на 10 часов позже текущего времени!")
            return
            
        # Get selected doping if any
        selected_doping = self.ui.comboBox_7.currentText()
        doping_id = None
        if selected_doping != "Выбор параметра":
            # Get doping ID from database
            conn = connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT DopingID FROM doping WHERE Doping = ?", (selected_doping,))
                result = cursor.fetchone()
                if result:
                    doping_id = result[0]
            except Exception as e:
                print(f"Error getting doping ID: {e}")
            finally:
                conn.close()
        else:
   
            doping_id = random.randint(1, 5)

        user_email = None
        if hasattr(self, 'log_email') and self.log_email:
            user_email = self.log_email
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить email пользователя. Пожалуйста, войдите в систему снова.")
            return

        flight_data = {
            'departure': f"{self.current_departure_airport['name']} ({self.current_departure_airport['code']})",
            'arrival': f"{self.current_arrival_airport['name']} ({self.current_arrival_airport['code']})",
            'time': self.ui.dateTimeEdit.dateTime().toString('dd.MM.yyyy HH:mm'),
            'price': f"{self.cash:.2f}",
            'user_email': user_email,
            'input_local_code': self.current_departure_airport['code'],
            'enter_local_code': self.current_arrival_airport['code'],
            'exit_time': self.ui.dateTimeEdit.dateTime().toString('yyyy-MM-dd HH:mm:ss'),
            'doping_id': doping_id
        }
        

        self.payment_window = pay_process.PaymentWindow(flight_data)
        self.payment_window.show()
    
    def zoom_in(self):
        if self.current_zoom < 17: 
            self.current_zoom += 1
            self.update_map_with_airports(force_zoom=self.current_zoom)
    
    def zoom_out(self):
        if self.current_zoom > 1:  
            self.current_zoom -= 1
            self.update_map_with_airports(force_zoom=self.current_zoom)
    
    def setup_combo_boxes(self):
        self.load_airport_data()
        self.load_doping_data()
        
        countries = sorted(list(self.country_city_map.keys()))
        for country in countries:
            self.ui.comboBox.addItem(country, country)
            self.ui.comboBox_4.addItem(country, country)
    
    def load_doping_data(self):
        cursor = connection().cursor()
        
        try:
            cursor.execute("SELECT Doping, DopingCost FROM doping")
            rows = cursor.fetchall()

            for row in rows:
                doping, doping_cost = row
                self.doping_data[doping] = doping_cost
            self.load_doping_data_on_combobox()
        except Exception as e: 
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные о допинге: {str(e)}")

    def load_doping_data_on_combobox(self):
        for i in self.doping_data:
            self.ui.comboBox_7.addItem(i)

    def load_airport_data(self):
        cursor = connection().cursor()
        try:
            cursor.execute("SELECT code, name, latitude, longitude, country, city FROM airports WHERE city IS NOT NULL AND city <> ''")
            rows = cursor.fetchall()
            
            for row in rows:
                code, name, lat, lon, country, city = row
                try:
                    lat_float = float(lat)
                    lon_float = float(lon)
                except (ValueError, TypeError):
                    continue
                
                self.airport_data.append({
                    'code': code,
                    'name': name,
                    'latitude': lat_float,
                    'longitude': lon_float,
                    'country': country,
                    'city': city
                })
                
                if city not in self.country_city_map[country]:
                    self.country_city_map[country].append(city)
                
                self.city_airport_map[city].append({
                    'code': code,
                    'name': name,
                    'lat': lat_float,
                    'lon': lon_float
                })
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные об аэропортах: {str(e)}")
    
    def update_cities_combo(self, index):
        if index == 0:  
            self.ui.comboBox_2.clear()
            self.ui.comboBox_3.clear()
            return
            
        country = self.ui.comboBox.currentData()
        self.ui.comboBox_2.clear()
        self.ui.comboBox_2.addItem('Город', None)
        
        if country in self.country_city_map:
            cities = sorted(self.country_city_map[country])
            for city in cities:
                self.ui.comboBox_2.addItem(city, city)
    
    def update_arrival_cities_combo(self, index):
        if index == 0:  
            self.ui.comboBox_5.clear()
            self.ui.comboBox_6.clear()
            return
            
        country = self.ui.comboBox_4.currentData()
        self.ui.comboBox_5.clear()
        self.ui.comboBox_5.addItem('Город', None)
        
        if country in self.country_city_map:
            cities = sorted(self.country_city_map[country])
            for city in cities:
                self.ui.comboBox_5.addItem(city, city)
    
    def update_departure_airports_combo(self, index):
        if index == 0: 
            self.ui.comboBox_3.clear()
            return
            
        city = self.ui.comboBox_2.currentData()
        self.ui.comboBox_3.clear()
        self.ui.comboBox_3.addItem('Аэропорт', None)
        
        if city in self.city_airport_map:
            airports = sorted(self.city_airport_map[city], key=lambda x: x['name'])
            for airport in airports:
                display_text = f"{airport['code']} - {airport['name']}"
                self.ui.comboBox_3.addItem(display_text, airport['code'])
    
    def update_arrival_airports_combo(self, index):
        if index == 0: 
            self.ui.comboBox_6.clear()
            return
            
        city = self.ui.comboBox_5.currentData()
        self.ui.comboBox_6.clear()
        self.ui.comboBox_6.addItem('Аэропорт', None)
        
        if city in self.city_airport_map:
            airports = sorted(self.city_airport_map[city], key=lambda x: x['name'])
            for airport in airports:
                display_text = f"{airport['code']} - {airport['name']}"
                self.ui.comboBox_6.addItem(display_text, airport['code'])
    
    def update_selected_departure_airport(self, index):
        if index == 0:  
            self.current_departure_airport = None
            self.update_map_with_airports()
            return
            
        airport_code = self.ui.comboBox_3.currentData()
        
        selected_airport = None
        for airport in self.airport_data:
            if airport['code'] == airport_code:
                selected_airport = airport
                break
                
        if selected_airport:
            self.current_departure_airport = selected_airport
            self.update_combos_to_match_airport(selected_airport, is_departure=True)
            self.update_map_with_airports()
            self.calculate_price_based_on_time()
    
    def update_selected_arrival_airport(self, index):
        if index == 0:  
            self.current_arrival_airport = None
            self.update_map_with_airports()
            return
            
        airport_code = self.ui.comboBox_6.currentData()
        
        selected_airport = None
        for airport in self.airport_data:
            if airport['code'] == airport_code:
                selected_airport = airport
                break
                
        if selected_airport:
            self.current_arrival_airport = selected_airport
            self.update_combos_to_match_airport(selected_airport, is_departure=False)
            self.update_map_with_airports()
            self.calculate_price_based_on_time()
    
    def update_combos_to_match_airport(self, airport, is_departure=True):
        if is_departure:
            self.ui.comboBox.blockSignals(True)
            self.ui.comboBox_2.blockSignals(True)
            
            country_index = self.ui.comboBox.findData(airport['country'])
            if country_index >= 0:
                self.ui.comboBox.setCurrentIndex(country_index)
                
                city_index = self.ui.comboBox_2.findData(airport['city'])
                if city_index >= 0:
                    self.ui.comboBox_2.setCurrentIndex(city_index)
            
            self.ui.comboBox.blockSignals(False)
            self.ui.comboBox_2.blockSignals(False)
        else:
            self.ui.comboBox_4.blockSignals(True)
            self.ui.comboBox_5.blockSignals(True)
            
            country_index = self.ui.comboBox_4.findData(airport['country'])
            if country_index >= 0:
                self.ui.comboBox_4.setCurrentIndex(country_index)
                
                city_index = self.ui.comboBox_5.findData(airport['city'])
                if city_index >= 0:
                    self.ui.comboBox_5.setCurrentIndex(city_index)
            
            self.ui.comboBox_4.blockSignals(False)
            self.ui.comboBox_5.blockSignals(False)

    def update(self):
        self.cash = self.money + (self.ui.spinBox.value() * 0.01)
        self.ui.label_12.setText(time.strftime("%H:%M:%S", time.gmtime(self.distance_km * 3.91)))
        self.ui.plainTextEdit.setPlainText(
            f'AVIATO COIN:\n {self.cash:.4f}\n'
            f'TON COIN:\n {self.cash:.4f}\n'
            f'BITCOIN:\n {(self.cash/29452):.4f}\n'
            f'RUB:\n {((self.cash/29452)*7500000):.1f}'
        )
    
    def update_map_with_airports(self, force_zoom=None):
        self.ui.label_8.setText("Загрузка карты...")
        self.ui.label_8.setAlignment(Qt.AlignCenter)
        
        if not self.current_departure_airport and not self.current_arrival_airport:
            self.load_initial_map()
            return
        
        if self.current_departure_airport and self.current_arrival_airport:
            try:
                dep_lat = float(self.current_departure_airport['latitude'])
                dep_lon = float(self.current_departure_airport['longitude'])
                arr_lat = float(self.current_arrival_airport['latitude'])
                arr_lon = float(self.current_arrival_airport['longitude'])
                
                distance = self.calculate_distance(dep_lat, dep_lon, arr_lat, arr_lon)
                
                if force_zoom is not None:
                    zoom = force_zoom
                else:
                    zoom = self.calculate_zoom_level(distance)
                    self.current_zoom = zoom
                
                padding_factor = min(0.3, 1000000 / max(distance, 1000))
                lon_span = abs(dep_lon - arr_lon) * (1 + padding_factor)
                lat_span = abs(dep_lat - arr_lat) * (1 + padding_factor)
                center_lon = (dep_lon + arr_lon) / 2
                center_lat = (dep_lat + arr_lat) / 2
                
                url = (f'https://static-maps.yandex.ru/v1?ll={center_lon},{center_lat}'
                       f'&lang=ru_RU&size=450,450&z={zoom}'
                       f'&pt={dep_lon},{dep_lat},pm2dbl1~{arr_lon},{arr_lat},pm2rdl2'
                       f'&pl=c:ff0000,w:4,{dep_lon},{dep_lat},{arr_lon},{arr_lat}'
                       f'&apikey=9ebc7a29-d936-473f-86f6-4993671ab8a0')
                
                self.distance_km = distance / 1000
                self.money = self.distance_km  
                self.calculate_price_based_on_time() 

            except (ValueError, TypeError) as e:
                QMessageBox.warning(self, "Ошибка", f"Некорректные координаты: {str(e)}")
                return
        elif self.current_departure_airport:
            try:
                lat = float(self.current_departure_airport['latitude'])
                lon = float(self.current_departure_airport['longitude'])
                zoom = force_zoom if force_zoom is not None else 13
                self.current_zoom = zoom
                url = f'https://static-maps.yandex.ru/v1?ll={lon},{lat}&lang=ru_RU&size=450,450&z={zoom}&pt={lon},{lat},pm2dbl1&apikey=9ebc7a29-d936-473f-86f6-4993671ab8a0'
            except (ValueError, TypeError) as e:
                self.ui.label_8.setText(f"Ошибка координат: {str(e)}")
                return
        else:
            try:
                lat = float(self.current_arrival_airport['latitude'])
                lon = float(self.current_arrival_airport['longitude'])
                zoom = force_zoom if force_zoom is not None else 13
                self.current_zoom = zoom
                url = f'https://static-maps.yandex.ru/v1?ll={lon},{lat}&lang=ru_RU&size=450,450&z={zoom}&pt={lon},{lat},pm2rdl2&apikey=9ebc7a29-d936-473f-86f6-4993671ab8a0'
            except (ValueError, TypeError) as e:
                self.ui.label_8.setText(f"Ошибка координат: {str(e)}")
                return
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                pixmap = QPixmap()
                if pixmap.loadFromData(QByteArray(response.content)):
                    self.ui.label_8.setPixmap(pixmap.scaled(
                        self.ui.label_8.size(), 
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    ))
                else:
                    self.ui.label_8.setText("Ошибка: неверные данные изображения")
            else:
                self.ui.label_8.setText(f"Ошибка загрузки карты (HTTP {response.status_code})")
        except requests.exceptions.RequestException as e:
            self.ui.label_8.setText(f"Ошибка сети: {str(e)}")
        except Exception as e:
            self.ui.label_8.setText(f"Ошибка: {str(e)}")
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000  
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def calculate_zoom_level(self, distance):
        """Improved zoom level calculation based on distance"""
        if distance < 5000:     # < 5 km
            return 11
        elif distance < 10000:   # 5-10 km
            return 10
        elif distance < 20000:   # 10-20 km
            return 9
        elif distance < 50000:   # 20-50 km
            return 8
        elif distance < 100000:  # 50-100 km
            return 7
        elif distance < 200000:  # 100-200 km
            return 6
        elif distance < 500000:  # 200-500 km
            return 5
        elif distance < 1000000: # 500-1000 km
            return 4
        elif distance < 2000000: # 1000-2000 km'
            return 3
        elif distance < 5000000: # 2000-5000 km
            return 2
        else:                    
            return 1
    
    def load_initial_map(self):
        self.ui.label_8.setText("Загрузка карты...")
        self.ui.label_8.setAlignment(Qt.AlignCenter)
        
        url = f'https://static-maps.yandex.ru/v1?ll=37.620070,55.753630&lang=ru_RU&size=450,450&z={self.current_zoom}&pt=37.620070,55.753630,pm2dbl1&apikey=9ebc7a29-d936-473f-86f6-4993671ab8a0'

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                pixmap = QPixmap()
                if pixmap.loadFromData(QByteArray(response.content)):
                    self.ui.label_8.setPixmap(pixmap.scaled(
                        self.ui.label_8.size(), 
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    ))
                else:
                    self.ui.label_8.setText("Ошибка: неверные данные изображения")
            else:
                self.ui.label_8.setText(f"Ошибка загрузки карты (HTTP {response.status_code})")
        except requests.exceptions.RequestException as e:
            self.ui.label_8.setText(f"Ошибка сети: {str(e)}")
        except Exception as e:
            self.ui.label_8.setText(f"Ошибка: {str(e)}")


def connection():
    try:
        return pyodbc.connect(
            "Driver={SQL Server};"
            "Server=KOMPUTER;"
            "Database=AVIATO_DB;" 
        )
    except Exception as e: 
        print(f"Ошибка подключения: {e}")
        return None