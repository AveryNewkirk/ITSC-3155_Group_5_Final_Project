from src.main import create_app
from flask_bcrypt import Bcrypt
import os
app = create_app()


if __name__ == '__main__':
    app.run()