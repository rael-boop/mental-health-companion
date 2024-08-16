import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URI = os.environ.get("DB_URL", "sqlite:///mhc.sqlite3")
    SECRET_KEY = os.environ.get("SECRET_KEY", 'development')
    DEBUG = bool(os.environ.get('DEBUG', 1))
    BCRYPT_SALT = int(os.environ.get('BCRYPT_SALT', 14))
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRATION_MINUTES = 50
    REFRESH_TOKEN_EXPIRATION_DAYS = 30
    PORT = int(os.environ.get("PORT", 8000))
    HF_TOKEN = os.environ.get("HF_TOKEN", 8000)

    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
    EMAIL_USER = os.environ.get("EMAIL_USER")
    EMAIL_SMTP_SERVER = os.environ.get("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 465))

    SENTIMENT_MODEL = "SamLowe/roberta-base-go_emotions"
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")
