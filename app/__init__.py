import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta


db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    app.permanent_session_lifetime = timedelta(minutes=30)
    
    os.makedirs(os.path.join(app.root_path, 'static/uploads'), exist_ok=True)
    
    from app.controllers.auth import auth_bp
    from app.controllers.posts import posts_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    
    with app.app_context():
        db.create_all()
    
    return app