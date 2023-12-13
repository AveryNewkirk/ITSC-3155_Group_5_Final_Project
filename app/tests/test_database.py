
from dotenv import load_dotenv
import os
from ..database import db
from flask import current_app



def test_connection(client):
    
    load_dotenv()
    
    assert db.engine.url.render_as_string(hide_password=False) == f'postgresql://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("TEST_DB_NAME")}'



