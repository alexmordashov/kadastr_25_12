from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Настройки почты
    MAIL_SERVER = 'smtp.yandex.ru'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'artembespechalov@yandex.ru'
    MAIL_PASSWORD = 'dzjniishqistktzd'
    MAIL_DEFAULT_SENDER = 'artembespechalov@yandex.ru'

    # Папка для загрузки файлов
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size