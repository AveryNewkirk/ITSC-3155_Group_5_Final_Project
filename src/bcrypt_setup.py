from flask_bcrypt import Bcrypt
import os

def init_bcrypt(app):
    app.secret_key = os.getenv('APP_SECRET_KEY', 'apple')
    bcrypt = Bcrypt()
    bcrypt.init_app(app)
    return bcrypt
