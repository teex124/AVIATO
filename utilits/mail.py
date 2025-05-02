import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_confirmation_email(receiver_email, confirmation_code):

    smtp_server = "smtp.mail.ru"
    smtp_port = 465
    sender_email = "aviato_group@mail.ru"
    sender_password = "zkDanT5bz126R9Sj8Fs0"  
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Код подтверждения"
    
    body = f"""
    Здравствуйте, вас беспокоит AVIATO GROUP
    
    Ваш код подтверждения: {confirmation_code}
    
    Никому не сообщайте этот код

    Мяу.
    """
    
    message.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        
        print(f"Код подтверждения {confirmation_code} успешно отправлен на {receiver_email}")
        return True
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")
        return False