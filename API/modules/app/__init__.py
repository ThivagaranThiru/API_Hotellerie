import datetime

from flask import Flask
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from modules.app.config import APP_CONFIG


MONGO = PyMongo()
MAIL = Mail()
JWT = JWTManager()
BCRYPT = Bcrypt()
BLACKLIST = set()

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)

    if isinstance(config_name, dict):
        app.config.update(config_name)
    else:
        app.config.from_object(APP_CONFIG[config_name])

    from modules.app.controllers.users import MODULE_USERS
    from modules.app.controllers.reservations import MODULE_RESERVATIONS
    from modules.app.controllers.hotels import MODULE_HOTELS

    app.register_blueprint(MODULE_USERS)
    app.register_blueprint(MODULE_RESERVATIONS)
    app.register_blueprint(MODULE_HOTELS)

    app.config.update(dict(
        DEBUG=True,
        MAIL_DEBUG=True,
        MAIL_SUPPRESS_SEND=False,
        MAIL_SERVER='smtp.gmail.com',
        TESTING=False,
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_USERNAME='mybookingservicecloud@gmail.com',
        MAIL_PASSWORD='passwordcloud',
        MAIL_DEFAULT_SENDER='mybookingservicecloud@gmail.com',
    ))

    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
    MONGO.init_app(app)
    MAIL.init_app(app)
    BCRYPT.init_app(app)
    JWT.init_app(app)

    app.app_context().push()

    return app
