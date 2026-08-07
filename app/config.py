import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nva-super-secret-key-change-in-production-2024'
    # Render/Heroku style DATABASE_URL; fallback to SQLite
    _db = os.environ.get('DATABASE_URL') or ''
    if _db.startswith('postgres://'):
        _db = _db.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db or (
        'sqlite:///' + os.path.join(os.path.dirname(basedir), 'instance', 'school.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'mp4', 'webm', 'svg'}
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'argonbhujel1@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'gygaxharvgvmmswd'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'argonbhujel1@gmail.com'
    
    # AI Auto Reply
    AI_AUTO_REPLY_ENABLED = True
    AI_AUTO_REPLY_WAIT_HOURS = 3  # Default 3 hours
    AI_TEMPLATES_PATH = os.path.join(basedir, 'services', 'ai_templates.json')
    
    # Firebase (for push notifications)
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS') or ''
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY') or ''
    
    # School defaults
    SCHOOL_NAME = "New Vision Academy"
    SCHOOL_PHONE = "+977-9841333476"
    
    # Pagination
    ITEMS_PER_PAGE = 12
    ADMIN_ITEMS_PER_PAGE = 20
    
    # Backup
    BACKUP_FOLDER = os.path.join(os.path.dirname(basedir), 'instance', 'backups')
    
    # Logging
    LOG_FOLDER = os.path.join(os.path.dirname(basedir), 'instance', 'logs')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
