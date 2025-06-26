import os
import sqlite3
import logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import event
from sqlalchemy.engine import Engine
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from re import compile
from config import config_by_name


db = SQLAlchemy()
login_manager = LoginManager()

# Ativa o uso de chaves estrangeiras no SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config_by_name[os.getenv('FLASK_ENV', 'dev')])

    # Configurações de Segurança
    app.config['SESSION_PERMANENT'] = True  # Torna a sessão não permanente
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)  # Sessão expira após 15 minutos de inatividade

    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0, proxy-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    # Pasta de logs
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # Caminho do log
    log_file = 'logs/lugarcerto.log'

    class RemoveAnsiFilter(logging.Filter):
        ansi_escape = compile(r'\x1b\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]')

        def filter(self, record):
            # Remove códigos ANSI da mensagem
            record.msg = self.ansi_escape.sub('', str(record.msg))
            return True

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Handler rotativo diário
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(RemoveAnsiFilter())

    # Para garantir que só um handler seja adicionado
    if not app.logger.handlers:
        app.logger.propagate = False
        app.logger.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    # Remove logs de /static no werkzeug
    class ExcludeStaticFilter(logging.Filter):
        def filter(self, record):
            return '/static/' not in record.getMessage()

    # Configura logger do werkzeug para gravar no arquivo também
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.INFO)
    # Evita múltiplos handlers repetidos
    if not any(isinstance(h, TimedRotatingFileHandler) for h in werkzeug_logger.handlers):
        werkzeug_logger.addFilter(ExcludeStaticFilter())
        werkzeug_logger.addHandler(file_handler)

        # Middleware para log customizado com IP, método e URL
        @app.before_request
        def log_request_info():
            if request.path.startswith('/static'):
                return  # não loga requisições de arquivos estáticos

            ip = request.remote_addr or 'desconhecido'
            method = request.method
            path = request.path
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            app.logger.info(f'{timestamp} - IP: {ip} - {method} {path}')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Pasta de upload
    upload_folder = app.config.get('UPLOAD_FOLDER') or os.path.join(app.root_path, 'static', 'imagens')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    # Blueprints
    from .routes.auth_routes import auth_bp
    from .routes.objeto_routes import objeto_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(objeto_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

        # Criar admin padrão a partir do .env
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@lugarcerto.com')
        admin_nome = os.getenv('ADMIN_NOME', 'Admin LugarCerto')
        admin_senha = os.getenv('ADMIN_SENHA', 'admin123')

        if not Usuario.query.filter_by(email=admin_email).first():
            admin = Usuario(
                nome=admin_nome,
                email=admin_email,
                senha=generate_password_hash(admin_senha),
                is_admin=True,
                aprovado=True
            )
            db.session.add(admin)
            db.session.commit()
            app.logger.info(f'Admin padrão criado: {admin_email}')

    return app
