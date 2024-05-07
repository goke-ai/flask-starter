from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import config_dic

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_dic[config_name])
    config_dic[config_name].init_app(app)
    
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    
    
    # attach routes and custom error pages here
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app


# from flask import Flask, request

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return 'Index Page'

# @app.route("/hello")
# def hello():
#     return "<p>Hello, World!</p>"