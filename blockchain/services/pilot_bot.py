import telebot
from telebot import types
import os
import cv2
import numpy as np
from threading import Thread
import time
from blockchain.services.wallet_service import WalletService

class FlightRequest:
    def __init__(self, user_email, flight_data):
        self.user_email = user_email
        self.flight_data = flight_data
        self.status = "pending"  # pending/accepted/declined/completed
        self.pilot_chat_id = None
        self.pilot_wallet = None
        self.pilot_payment = float(flight_data.get('price', 0)) * 0.1

class PilotBot:
    def __init__(self, wallet_service):
        self.wallet_service = wallet_service
        self.bot = None
        self.admin_wallet = "XJ2Y34MNFR"
        self.running = False
        self.flight_requests = {}  
        self.pilot_wallets = {}    
        self.token = None

    def initialize_bot(self, token):
        """Initialize the Telegram bot with token"""
        try:
            self.token = token
            self.bot = telebot.TeleBot(token)
            print("Bot initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing bot: {e}")
            return False

    def start_bot(self):
        """Start the bot polling in a separate thread"""
        if not self.bot:
            if not self.initialize_bot(self.token):
                return False
            
        self.running = True
        
        def polling():
            while self.running:
                try:
                    print("Starting bot polling...")
                    self.bot.polling(none_stop=True, interval=3, timeout=20)
                except Exception as e:
                    print(f"Bot polling error: {e}")
                    time.sleep(5)
            
        self.polling_thread = Thread(target=polling, daemon=True)
        self.polling_thread.start()
        return True

    def stop_bot(self):
        """Stop the bot polling"""
        self.running = False
        if self.bot:
            self.bot.stop_polling()

    def setup_handlers(self):
        """Setup all bot handlers"""
        if not self.bot:
            return

        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.bot.reply_to(
                message,
                "✈️ Добро пожаловать в бот для пилотов AVIATO!\n\n"
                "Здесь вы будете получать уведомления о новых заказах. "
                "Когда поступит новый заказ, вы сможете принять или отклонить его."
            )
            if message.chat.id in self.pilot_wallets:
                self.bot.send_message(
                    message.chat.id,
                    f"Ваш текущий кошелек: {self.pilot_wallets[message.chat.id]}"
                )

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_all_callbacks(call):
            if call.data.startswith(('accept_', 'decline_', 'cancel_', 'confirm_')):
                self.handle_pilot_response(call)

    def create_keyboard(self, buttons):
        """Create inline keyboard from list of (text, callback_data) tuples"""
        keyboard = types.InlineKeyboardMarkup()
        for text, callback in buttons:
            keyboard.add(types.InlineKeyboardButton(text=text, callback_data=callback))
        return keyboard

    def send_flight_notification(self, chat_id, flight_data):
        """Send flight notification to pilot"""
        if not self.bot:
            print("Bot not initialized")
            return False
            
        try:
            user_email = flight_data['user_email']
            
            # Create new flight request
            self.flight_requests[user_email] = FlightRequest(user_email, flight_data)
            request = self.flight_requests[user_email]
            
            message = (
                f"🛫 Новый заказ на полет!\n\n"
                f"📧 Клиент: {user_email}\n"
                f"💰 Ваш заработок: {request.pilot_payment:.2f} AVIATO COIN\n"
                f"🛩 Входной код: {flight_data.get('input_local_code', 'N/A')}\n"
                f"🛬 Выходной код: {flight_data.get('enter_local_code', 'N/A')}\n"
                f"⏰ Время выхода: {flight_data.get('exit_time', 'N/A')}\n\n"
                f"Примите или отклоните заказ:"
            )
            
            # Send message with buttons
            self.bot.send_message(
                chat_id,
                message,
                reply_markup=self.create_keyboard([
                    ("✅ Принять заказ", f"accept_{user_email}"),
                    ("❌ Отказаться", f"decline_{user_email}")
                ])
            )
            return True
                
        except Exception as e:
            print(f"Ошибка при отправке уведомления: {str(e)}")
            return False

    def handle_pilot_response(self, call):
        """Handle pilot's response to flight offer"""
        if not self.bot or not self.wallet_service:
            print("Services not initialized")
            return

        try:
            action, user_email = call.data.split('_', 1)
            pilot_chat_id = call.message.chat.id

            if user_email not in self.flight_requests:
                self.bot.answer_callback_query(call.id, "❌ Заказ больше не доступен")
                return

            request = self.flight_requests[user_email]

            if action == "accept":
                request.status = "accepted"
                request.pilot_chat_id = pilot_chat_id
                
                if pilot_chat_id in self.pilot_wallets:
                    request.pilot_wallet = self.pilot_wallets[pilot_chat_id]
                    self._confirm_accepted_order(request)
                else:
                    msg = self.bot.send_message(
                        pilot_chat_id,
                        "✈️ Вы приняли заказ!\n\n"
                        "Пожалуйста, введите номер вашего кошелька AVIATO ZENPAY:",
                        reply_markup=self.create_keyboard([
                            ("❌ Отменить", f"cancel_{user_email}")
                        ])
                    )
                    self.bot.register_next_step_handler(msg, self.process_pilot_wallet, user_email)
                
                self.bot.edit_message_text(
                    f"✅ Вы приняли заказ от {user_email}\n"
                    f"Ожидается ввод вашего кошелька",
                    pilot_chat_id,
                    call.message.message_id
                )
                
            elif action == "decline":
                request.status = "declined"
                self.bot.edit_message_text(
                    "❌ Вы отказались от заказа\n\n"
                    "Спасибо за ваш ответ!",
                    pilot_chat_id,
                    call.message.message_id
                )
            elif action == "cancel":
                request.status = "pending"
                self.bot.edit_message_text(
                    "❌ Вы отменили принятие заказа",
                    pilot_chat_id,
                    call.message.message_id
                )
            elif action == "confirm":
                self.handle_arrival_confirmation(call)
                
        except Exception as e:
            print(f"Error handling pilot response: {e}")
            self.bot.answer_callback_query(call.id, "❌ Ошибка обработки запроса")

    def process_pilot_wallet(self, message, user_email):
        """Process pilot's wallet input"""
        if not self.bot or not self.wallet_service:
            return

        try:
            pilot_chat_id = message.chat.id
            wallet_address = message.text.strip()
            
            if user_email not in self.flight_requests:
                self.bot.send_message(pilot_chat_id, "❌ Заказ больше не доступен")
                return

            request = self.flight_requests[user_email]
            
            if not wallet_address or len(wallet_address) < 5:
                msg = self.bot.send_message(
                    pilot_chat_id,
                    "❌ Неверный формат кошелька. Пожалуйста, введите корректный номер:",
                    reply_markup=self.create_keyboard([
                        ("❌ Отменить", f"cancel_{user_email}")
                    ])
                )
                self.bot.register_next_step_handler(msg, self.process_pilot_wallet, user_email)
                return
                
            request.pilot_wallet = wallet_address
            self.pilot_wallets[pilot_chat_id] = wallet_address
            self._confirm_accepted_order(request)
            
        except Exception as e:
            print(f"Error processing wallet: {e}")
            self.bot.send_message(message.chat.id, "❌ Ошибка обработки кошелька")

    def _confirm_accepted_order(self, request):
        """Confirm order acceptance and show arrival button"""
        self.bot.send_message(
            request.pilot_chat_id,
            f"✅ Кошелек успешно привязан!\n\n"
            f"Кошелек: {request.pilot_wallet}\n"
            f"Сумма к оплате: {request.pilot_payment:.2f} AVIATO COIN\n\n"
            f"После выполнения полета подтвердите прибытие:",
            reply_markup=self.create_keyboard([
                ("🛬 Подтвердить выполнение", f"confirm_{request.user_email}"),
                ("❌ Отменить заказ", f"cancel_{request.user_email}")
            ])
        )

    def handle_arrival_confirmation(self, call):
        """Handle pilot's arrival confirmation"""
        if not self.bot or not self.wallet_service:
            return

        try:
            action, user_email = call.data.split('_', 1)
            pilot_chat_id = call.message.chat.id

            if user_email not in self.flight_requests:
                self.bot.answer_callback_query(call.id, "❌ Заказ не найден")
                return

            request = self.flight_requests[user_email]

            if action == "confirm":
                msg = self.bot.send_message(
                    pilot_chat_id,
                    "📸 Сделайте фото самолета для подтверждения:",
                    reply_markup=self.create_keyboard([
                        ("❌ Отменить", f"cancel_{user_email}")
                    ])
                )
                self.bot.register_next_step_handler(msg, self.process_confirmation_photo, user_email)
                
                self.bot.edit_message_text(
                    f"🛬 Ожидается фото подтверждение для {user_email}",
                    pilot_chat_id,
                    call.message.message_id
                )
                
        except Exception as e:
            print(f"Error handling confirmation: {e}")
            self.bot.answer_callback_query(call.id, "❌ Ошибка подтверждения")

    def process_confirmation_photo(self, message, user_email):
        """Process confirmation photo from pilot"""
        if not self.bot or not self.wallet_service:
            return

        pilot_chat_id = message.chat.id
        
        try:
            if user_email not in self.flight_requests:
                self.bot.send_message(pilot_chat_id, "❌ Заказ не найден")
                return

            request = self.flight_requests[user_email]
            
            if not message.photo and not (message.document and 
                                        message.document.mime_type.startswith('image/')):
                msg = self.bot.send_message(
                    pilot_chat_id,
                    "❌ Пожалуйста, отправьте именно фото (JPEG/PNG):",
                    reply_markup=self.create_keyboard([
                        ("❌ Отменить", f"cancel_{user_email}")
                    ])
                )
                self.bot.register_next_step_handler(msg, self.process_confirmation_photo, user_email)
                return
                
            try:
                if message.photo:
                    file_id = message.photo[-1].file_id
                else:
                    file_id = message.document.file_id
                    
                file_info = self.bot.get_file(file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)
                
                photo_path = f"temp_confirm_{user_email}.jpg"
                with open(photo_path, 'wb') as f:
                    f.write(downloaded_file)
                    
                if self._verify_photo(photo_path):
                    if self._process_payment(request):
                        request.status = "completed"
                        self.bot.send_message(
                            pilot_chat_id,
                            f"✅ Проверка пройдена!\n\n"
                            f"💸 На ваш кошелек {request.pilot_wallet} "
                            f"переведено {request.pilot_payment:.2f} AVIATO COIN"
                        )
                    else:
                        self.bot.send_message(
                            pilot_chat_id,
                            "❌ Ошибка перевода средств. Обратитесь в поддержку."
                        )
                else:
                    msg = self.bot.send_message(
                        pilot_chat_id,
                        "❌ Фото не прошло проверку. Отправьте другое фото (должно быть цветное, не слишком маленькое):",
                        reply_markup=self.create_keyboard([
                            ("❌ Отменить", f"cancel_{user_email}")
                        ])
                    )
                    self.bot.register_next_step_handler(msg, self.process_confirmation_photo, user_email)
                    
            except Exception as e:
                print(f"Error processing photo: {e}")
                self.bot.send_message(pilot_chat_id, "❌ Ошибка обработки фото. Попробуйте еще раз.")
                
            finally:
                try:
                    os.remove(photo_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"Error in photo handler: {e}")
            self.bot.send_message(pilot_chat_id, "❌ Ошибка обработки запроса")

    def _verify_photo(self, photo_path):
        """Verify the confirmation photo contains an airplane"""
        try:
            img = cv2.imread(photo_path)
            if img is None:
                return False

            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lower_white = np.array([0, 0, 200], dtype=np.uint8)
            upper_white = np.array([255, 30, 255], dtype=np.uint8)
            white_mask = cv2.inRange(hsv, lower_white, upper_white)

            matching_pixels = cv2.countNonZero(white_mask)
            total_pixels = img.shape[0] * img.shape[1]
            percentage = (matching_pixels / total_pixels) * 100
            
            return percentage > 20

        except Exception as e:
            print(f"Ошибка при проверке фото: {e}")
            return False

    def _process_payment(self, request):
        wallet_service = WalletService()
        return wallet_service.transfer_coins(
            self.admin_wallet,
            request.pilot_wallet,
            request.pilot_payment
        )
    
        
    def bot_iter(self, payment_data):
        """Основной метод для отправки уведомления (без дублирования)"""
        try:
            class Args:
                def __init__(self, data):
                    self.user_email = data['user_email']
                    self.cost = str(data['cost'])
                    self.input_local_code = data['input_local_code']
                    self.enter_local_code = data['enter_local_code']
                    self.exit_time = data['exit_time']

            args = Args(payment_data)
            self._send_notification(args)  # Используем единый метод отправки

        except Exception as e:
            print(f"❌ Ошибка в bot_iter: {e}")
            raise

    def _send_notification(self, args):
        """Единый метод отправки уведомления"""
        try:
            bot_token = "7986897170:AAFxujD1FQNsANvQdh3phV0Yz4QLLUxDi5w"
            test_chat_id = "6253156519"
            
            test_data = {
                'user_email': args.user_email,
                'price': args.cost,
                'input_local_code': args.input_local_code,
                'enter_local_code': args.enter_local_code,
                'exit_time': args.exit_time
            }

            # Создаем бота только если он еще не инициализирован
            if not hasattr(self, '_bot_instance'):
                self._bot_instance = PilotBot(self.wallet_service)
                if self._bot_instance.initialize_bot(bot_token):
                    self._bot_instance.setup_handlers()
                    self._bot_instance.start_bot()

            # Отправляем уведомление
            self._bot_instance.send_flight_notification(test_chat_id, test_data)

        except Exception as e:
            print(f"❌ Ошибка при отправке: {e}")