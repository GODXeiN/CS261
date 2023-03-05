from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME="database.db"
app= Flask(__name__)

def create_app():
    app.config['SECRET_KEY'] = '7:L3~`*t-7r(,}.AJnjBu!Jh~@cE@cchz<wr-.&8BsC&RY&SW'
    app.config['SQLALCHEMY_DATABASE_URI']=f'sqlite:///{DB_NAME}'
    db.init_app(app)


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from . import models

    login_manager=LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(id):
        return models.Manager.query.get(int(id))  
    return app

    
    

