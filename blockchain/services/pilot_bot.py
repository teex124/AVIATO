import telebot
from telebot import types
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import requests
from ..core.database import Database
from ..services.wallet_service import WalletService


load_dotenv()


BOT_TOKEN = "7986897170:AAFxujD1FQNsANvQdh3phV0Yz4QLLUxDi5w"  
ADMIN_WALLET = "XJ2Y34MNFR" 
PILOT_CHAT_ID = "6253156519"  

try:
    bot = telebot.TeleBot(BOT_TOKEN)
except Exception as e:
    print(f"Error initializing bot: {e}")
    bot = None


flight_requests = {}
pilot_wallets = {}

class PilotBot:
    def __init__(self):
        self.db = Database()
        self.wallet_service = WalletService()
        self.pilot_chat_id = PILOT_CHAT_ID
        self.bot = bot

    def get_flight_keyboard(self, flight_data):
        keyboard = types.InlineKeyboardMarkup()
        accept_btn = types.InlineKeyboardButton(text="Принять", callback_data=f"accept_{flight_data.get('user_email', '')}")
        decline_btn = types.InlineKeyboardButton(text="Отказать", callback_data=f"decline_{flight_data.get('user_email', '')}")
        keyboard.add(accept_btn, decline_btn)
        return keyboard

    def send_flight_notification(self, chat_id, flight_data, send_photo=True):
        if not self.bot:
            print("Bot not initialized")
            return
            
        try:
            flight_cost = float(flight_data.get('price', 0))
            pilot_payment = flight_cost * 0.1
            
            message = (
                f"🛩 Новый заказ на полет!\n\n"
                f"Откуда: {flight_data.get('departure', 'N/A')}\n"
                f"Куда: {flight_data.get('arrival', 'N/A')}\n"
                f"Время: {flight_data.get('time', 'N/A')}\n"
                f"Стоимость: {flight_data.get('price', 'N/A')} AVIATO COIN\n"
                f"Оплата пилоту: {pilot_payment:.2f} AVIATO COIN\n"
            )
            

            flight_requests[flight_data.get('user_email', '')] = {
                'data': flight_data,
                'pilot_payment': pilot_payment,
                'status': 'pending'
            }
            
            if send_photo and 'photo_path' in flight_data:
                try:
                    with open(flight_data['photo_path'], 'rb') as photo:
                        self.bot.send_photo(
                            chat_id,
                            photo,
                            caption=message,
                            reply_markup=self.get_flight_keyboard(flight_data)
                        )
                except Exception as e:
                    print(f"Ошибка при отправке фото: {str(e)}")
                    self.bot.send_message(
                        chat_id,
                        message,
                        reply_markup=self.get_flight_keyboard(flight_data)
                    )
            else:
                self.bot.send_message(
                    chat_id,
                    message,
                    reply_markup=self.get_flight_keyboard(flight_data)
                )
                
        except Exception as e:
            print(f"Ошибка при отправке уведомления: {str(e)}")

    def handle_pilot_response(self, call):
        if not bot:
            print("Bot not initialized, cannot handle response")
            return

        try:
            action, user_email = call.data.split('_')
            
            if action == "accept":
                msg = bot.send_message(
                    call.message.chat.id,
                    "Введите номер кошелька AVIATO ZENPAY:"
                )
                bot.register_next_step_handler(msg, self.process_pilot_wallet, user_email)
            else:
                flight_requests[user_email]['status'] = 'declined'
                bot.edit_message_text(
                    "Вы отказались от полета",
                    call.message.chat.id,
                    call.message.message_id
                )
        except Exception as e:
            print(f"Error handling pilot response: {e}")

    def process_pilot_wallet(self, message, user_email):
        
        if not bot:
            print("Bot not initialized, cannot process wallet")
            return

        try:
            pilot_wallet = message.text.strip()
            
        
            pilot_wallets[user_email] = pilot_wallet
            
            flight_data = flight_requests[user_email]
            
            
            self.wallet_service.transfer_coins(
                ADMIN_WALLET,
                pilot_wallet,
                flight_data['pilot_payment']
            )
            
            flight_requests[user_email]['status'] = 'accepted'
            
            
            bot.send_message(
                message.chat.id,
                f"Деньги успешно переведены на ваш кошелек!\n"
                f"Сумма: {flight_data['pilot_payment']:.2f} AVIATO COIN"
            )
            
            
            self.db.execute(
                "UPDATE pays SET pilot_wallet = ?, status = 'accepted' WHERE user_email = ?",
                (pilot_wallet, user_email)
            )
            
        except Exception as e:
            print(f"Error processing pilot wallet: {e}")
            if bot:
                bot.send_message(
                    message.chat.id,
                    f"Ошибка при переводе денег: {str(e)}"
                )

def start_bot():
    
    if not bot:
        print("Bot not initialized, cannot start")
        return

    pilot_bot = PilotBot()
    
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        bot.reply_to(message, "Добро пожаловать! Я бот для пилотов AVIATO.")

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        pilot_bot.handle_pilot_response(call)

    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error starting bot: {e}")

if __name__ == "__main__":
    start_bot() 