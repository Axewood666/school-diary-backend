from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.core.config import settings


class MailerService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME = settings.MAIL_USERNAME,
            MAIL_PASSWORD = settings.MAIL_PASSWORD,
            MAIL_FROM = settings.MAIL_FROM,
            MAIL_PORT = settings.MAIL_PORT,
            MAIL_SERVER = settings.MAIL_SERVER,
            MAIL_STARTTLS = settings.MAIL_STARTTLS,
            MAIL_SSL_TLS = settings.MAIL_SSL_TLS,
            USE_CREDENTIALS = settings.USE_CREDENTIALS,
            VALIDATE_CERTS = settings.VALIDATE_CERTS
        )
    
    async def send_email(self, email: EmailStr, subject: str, body: str):
        try:
            message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype="html"
            )
            fm = FastMail(self.conf)
            await fm.send_message(message)
            return True
        except Exception as e:
            return False
        

mailer_service = MailerService()

def get_mailer_service() -> MailerService:
    return mailer_service