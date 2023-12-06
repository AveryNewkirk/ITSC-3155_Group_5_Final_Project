from flask import Flask
import os, base64
from dotenv import load_dotenv
from .database import *
from sqlalchemy import text
from src.bcrypt_setup import init_bcrypt
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt();


def create_app():
    app = Flask(__name__)
    
    load_dotenv()

    #app.secret_key = os.getenv('APP_SECRET_KEY', 'apple')

    #database connection
    app.config["SQLALCHEMY_DATABASE_URI"] = \
    f'postgresql://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
    app.config['SQLAlCHEMY_ECHO'] = True
    app.config['SECRET_KEY'] = 'apples'
    app.config['SESSION_COOKIE_PATH'] = '/'

    db.init_app(app)
    bcrypt.init_app(app)
    #Validate database connection
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            print(f'\n\tSuccessful connection to {os.getenv("DB_USERNAME")}\n')
        except Exception as e:
            print(f"\nConnection failed. ERROR:{e}")

    # Jinja filter for encoding bytes into base64, readable in the src attribute of an img tag
    app.jinja_env.filters['b64encode'] = b64encode_filter

    # from .routes import route_1, route_2, ...
    from .routes import (
        index_routes, # Riley
        login_routes,
        profile_routes,
        settings_routes,
        sell_routes, # Riley
        listing_routes, # Riley
        community_routes,
        contact_routes,
        user_routes,
        marketplace_routes,
        signup
    )
    
    app.register_blueprint(index_routes.index)
    app.register_blueprint(login_routes.login)
    app.register_blueprint(profile_routes.profile)
    app.register_blueprint(settings_routes.settings)
    app.register_blueprint(sell_routes.sell)
    app.register_blueprint(listing_routes.listing)
    app.register_blueprint(community_routes.community)
    app.register_blueprint(contact_routes.contact)
    app.register_blueprint(user_routes.user)
    app.register_blueprint(marketplace_routes.marketplace)
    app.register_blueprint(signup.signup)

    return app

def b64encode_filter(data):
    return base64.b64encode(data).decode('ascii') if data else ''