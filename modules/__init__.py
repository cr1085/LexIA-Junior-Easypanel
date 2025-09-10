from flask import Flask
from flask_login import LoginManager
import os
import click
from .auth.models import User, init_db
from config import Config
from .assistant.rag_processor import RAGProcessor

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_object(Config)
    
    app.secret_key = app.config.get('SECRET_KEY', 'dev-key-shhh-this-is-secret')
    
    app.rag_processor = RAGProcessor()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Registrar Blueprints
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from .main.routes import main_bp
    app.register_blueprint(main_bp)

    from .assistant.routes import assistant_bp
    app.register_blueprint(assistant_bp)
    
    from .documents.routes import documents_bp
    app.register_blueprint(documents_bp)
    
    # --- CAMBIO AQUÍ: Registramos el nuevo blueprint de admin ---
    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp)
    # --- FIN DEL CAMBIO ---
    
    @app.cli.command('init-db')
    def init_db_command():
        init_db()
        click.echo('Base de datos inicializada.')

    return app