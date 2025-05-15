import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
import datetime


def send_confirmation_email(receiver_email, confirmation_code):

    smtp_server = "smtp.mail.ru"
    smtp_port = 465
    sender_email = "aviato_group@mail.ru"
    sender_password = "zkDanT5bz126R9Sj8Fs0"  
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Код подтверждения AVIATO GROUP"
    

    body = f"""
    <html>
      <head>
        <style>
          body {{
            font-family: sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
          }}
          .container {{
            background-color: #ffffff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: auto;
          }}
          .header {{
            color: #333333;
            text-align: center;
            border-bottom: 1px solid #eeeeee;
            padding-bottom: 20px;
          }}
          .code {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
            text-align: center;
            margin: 30px 0;
            padding: 15px;
            background-color: #e7f3ff;
            border: 1px dashed #007bff;
            border-radius: 4px;
          }}
          .footer {{
            text-align: center;
            font-size: 12px;
            color: #777777;
            margin-top: 30px;
          }}
          .logo-placeholder {{
            text-align: center;
            margin-bottom: 20px;
            font-size: 28px;
            font-weight: bold;
            color: #0056b3; /* Darker blue for logo */
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="logo-placeholder">AVIATO GROUP</div>
          <div class="header">
            <h2>Подтверждение вашей электронной почты</h2>
          </div>
          <p>Здравствуйте,</p>
          <p>Спасибо за регистрацию в AVIATO GROUP. Пожалуйста, используйте следующий код для подтверждения вашей учетной записи:</p>
          <div class="code">{confirmation_code}</div>
          <p>Этот код действителен в течение ограниченного времени. Если вы не запрашивали этот код, пожалуйста, проигнорируйте это письмо.</p>
          <p>С наилучшими пожеланиями,<br>Команда AVIATO GROUP</p>
          <div class="footer">
            <p>Это автоматическое сообщение, пожалуйста, не отвечайте на него.</p>
            <p>&copy; {datetime.date.today().year} AVIATO GROUP. Все права защищены.</p>
          </div>
        </div>
      </body>
    </html>
    """
    
    message.attach(MIMEText(body, "html"))
    
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        
        print(f"Код подтверждения {confirmation_code} успешно отправлен на {receiver_email}")
        return True
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")
        return False

def send_receipt_email(receiver_email, payment_data):
    smtp_server = "smtp.mail.ru"
    smtp_port = 465
    sender_email = "aviato_group@mail.ru"
    sender_password = "zkDanT5bz126R9Sj8Fs0"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Чек об оплате AVIATO GROUP"


    body = f"""
    <html>
      <head>
        <style>
          body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; color: #333; }}
          .container {{ width: 100%; max-width: 600px; margin: 20px auto; background-color: #fff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
          .header {{ background-color: #0056b3; color: #ffffff; padding: 20px; text-align: center; border-top-left-radius: 8px; border-top-right-radius: 8px; }}
          .header h1 {{ margin: 0; font-size: 24px; }}
          .content {{ padding: 30px; }}
          .content h2 {{ color: #0056b3; font-size: 20px; margin-top: 0; }}
          .info-table {{ width: 100%; margin-bottom: 20px; border-collapse: collapse; }}
          .info-table td {{ padding: 10px; border-bottom: 1px solid #eeeeee; }}
          .info-table td:first-child {{ font-weight: bold; color: #555; width: 40%; }}
          .total {{ text-align: right; font-size: 18px; font-weight: bold; margin-top: 20px; }}
          .total span {{ color: #0056b3; }}
          .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777777; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; background-color: #f9f9f9; }}
          .logo-placeholder {{ text-align: center; margin-bottom: 10px; font-size: 28px; font-weight: bold; color: #0056b3; }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>Чек об оплате</h1>
          </div>
          <div class="content">
            <div class="logo-placeholder">AVIATO GROUP</div>
            <h2>Детали вашего заказа:</h2>
            <table class="info-table">
              <tr><td>Email покупателя:</td><td>{receiver_email}</td></tr>
              <tr><td>Пункт вылета:</td><td>{payment_data.get('input_local_code', 'N/A')}</td></tr>
              <tr><td>Пункт назначения:</td><td>{payment_data.get('enter_local_code', 'N/A')}</td></tr>
              <tr><td>Время вылета:</td><td>{payment_data.get('exit_time', 'N/A')}</td></tr>
              <tr><td>Стоимость:</td><td>{payment_data.get('cost', 'N/A')} AVIATO COIN</td></tr>
            </table>
            <div class="total">
              Итого к оплате: <span>{payment_data.get('cost', 'N/A')} AVIATO COIN</span>
            </div>
            <p>Спасибо за покупку!</p>
          </div>
          <div class="footer">
            <p>Это автоматическое сообщение, пожалуйста, не отвечайте на него.</p>
            <p>&copy; {datetime.date.today().year} AVIATO GROUP. Все права защищены.</p>
          </div>
        </div>
      </body>
    </html>
    """
    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Чек об оплате успешно отправлен на {receiver_email}")
        return True
    except Exception as e:
        print(f"Ошибка при отправке email с чеком: {e}")
        return False
    
