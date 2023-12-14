from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_uploads import UploadSet, IMAGES

load_dotenv()
class Config(object):
    TESTING = False

    scrap_code = True

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False



class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI= f'postgresql://{os.getenv("TEST_DB_USERNAME")}:{os.getenv("TEST_DB_PASSWORD")}@{os.getenv("TEST_DB_HOST")}:{os.getenv("TEST_DB_PORT")}/{os.getenv("TEST_DB_NAME")}'


photos = UploadSet('photos', IMAGES)

PHOTOS_PATH = 'user_images/'