from flask import Flask
import os 
from dotenv import load_dotenv
from .database import db
from sqlalchemy import text



def create_app():
    app = Flask(__name__)
    
    load_dotenv()

    #database connection
    app.config["SQLALCHEMY_DATABASE_URI"] = \
    f'postgresql://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
    app.config['SQLAlCHEMY_ECHO'] = True

    db.init_app(app)

    #Validate database connection
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            print(os.getenv("DB_USERNAME"))
            print(os.getenv("DB_PASSWORD"))
            print(os.getenv("DB_HOST"))
            print(os.getenv("DB_PORT"))
            print(os.getenv("DB_NAME"))
            print('Successful connection')
        except Exception as e:
            print(f"Connection failed. ERROR:{e}")



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
        marketplace_routes
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
    
    return app