import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_migrate import Migrate
from app.config import config
from app.models import db, User

login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
migrate = Migrate()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__, instance_relative_config=True)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    app.config.from_object(config.get(config_name, config['default']))
    
    # Ensure instance folders
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config.get('BACKUP_FOLDER', os.path.join(app.instance_path, 'backups')), exist_ok=True)
    os.makedirs(app.config.get('LOG_FOLDER', os.path.join(app.instance_path, 'logs')), exist_ok=True)
    
    # Sub upload folders
    for sub in ['slider', 'gallery', 'staff', 'news', 'blogs', 'facilities', 'logos', 'notices', 'downloads']:
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], sub), exist_ok=True)
    
    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    print(f"MAIL configured: server={app.config.get('MAIL_SERVER')} user={app.config.get('MAIL_USERNAME')}")
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.blueprints.public import public_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.auth import auth_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    @app.template_filter('media')
    def media_filter(path):
        try:
            from app.utils.helpers import media_url
            return media_url(path) or ''
        except Exception:
            if not path:
                return ''
            path = str(path)
            if path.startswith('http'):
                return path
            return '/uploads/' + path.lstrip('/')

    # Context processors
    @app.context_processor
    def inject_globals():
        from app.models import SchoolSetting, Notice
        settings = {}
        try:
            for s in SchoolSetting.query.all():
                settings[s.key] = s.value
        except:
            pass
        latest_notices = []
        try:
            latest_notices = Notice.query.filter_by(is_active=True).order_by(Notice.is_pinned.desc(), Notice.publish_date.desc()).limit(5).all()
        except:
            pass
        return {
            'school_settings': settings,
            'latest_notices_ticker': latest_notices,
            'school_name': settings.get('school_name', 'New Vision Academy'),
            'school_phone': settings.get('phone', '+977-9841333476'),
            'school_email': settings.get('display_email') or settings.get('email', 'info@newvisionacademy.edu.np'),
            'smtp_email': settings.get('email', 'argonbhujel1@gmail.com'),
            'school_address': settings.get('address', 'Urlabari-8, Morang, Koshi Province, Nepal'),
            'whatsapp_number': settings.get('whatsapp', '9779841333476'),
            'school_lat': settings.get('latitude', '26.64513162062879'),
            'school_lng': settings.get('longitude', '87.63686430000001'),
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('public/pages/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        import traceback
        print('=== 500 ERROR ===')
        traceback.print_exc()
        from flask import render_template
        return render_template('public/pages/500.html'), 500
    
    # Create tables and seed
    with app.app_context():
        db.create_all()
        from app.utils.seed import seed_database
        seed_database()
    
    # Start AI background checker (simple scheduler)
    try:
        from app.services.ai_reply import start_ai_scheduler
        start_ai_scheduler(app)
    except Exception as e:
        print(f"AI scheduler note: {e}")
    
    return app
