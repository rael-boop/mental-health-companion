import smtplib
import ssl
from src.config import Config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Emailer:

    def __init__(self):
        self.smtp_server = Config.EMAIL_SMTP_SERVER
        self.port = Config.EMAIL_PORT
        self.context = ssl.create_default_context()
        self.sender_email = Config.EMAIL_USER
        self.sender_password = Config.EMAIL_PASSWORD

    def create_message(
        self, recipient_email: str, message: str, subject: str, is_html=False
    ):
        """Creates a MIMEMultipart message with plain text or HTML content.

        Args:
            message: The message content.
            subject: The email subject.
            is_html: Set to True for HTML content, \
                False for plain text (default).

        Returns:
            A MIMEMultipart email message object.
        """

        message_obj = MIMEMultipart("alternative" if is_html else "plain")
        message_obj["Subject"] = subject
        message_obj["From"] = self.sender_email
        message_obj["To"] = recipient_email

        text_part = MIMEText(message, "plain" if not is_html else "html")
        message_obj.attach(text_part)

        return message_obj

    def send_email(
        self, recipient_email: str,  message: str, subject: str, is_html=False
    ):
        """Sends an email with the specified message, subject, and recipient.

        Args:
            message: The message content.
            subject: The email subject.
            recipient_email: The recipient's email address.
            is_html: Set to True for HTML content, \
                False for plain text (default).
        """
        message_obj = self.create_message(
            recipient_email=recipient_email,
            message=message,
            subject=subject,
            is_html=is_html
        )

        with smtplib.SMTP_SSL(
            self.smtp_server, self.port, context=self.context
        ) as smtp:
            smtp.login(self.sender_email, self.sender_password)
            smtp.sendmail(
                self.sender_email, recipient_email, message_obj.as_string()
            )
