from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_uploads import UploadSet, IMAGES

class Config(object):
    scrap_code = True

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

photos = UploadSet('photos', IMAGES)

PHOTOS_PATH = 'user_images/'