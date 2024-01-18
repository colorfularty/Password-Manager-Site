from os import path
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
DB_NAME = "database.db"

def createApp():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "fgeiwerjyndcfgv"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)
    
    from .views import views
    app.register_blueprint(views, url_prefix="/")

    # Make sure database is created if it doesn't already exist
    if not path.exists(DB_NAME):
        with app.app_context():
            db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "views.login"
    login_manager.init_app(app)
    
    from .models import User

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app