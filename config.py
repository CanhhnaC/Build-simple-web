import os
from dotenv import load_dotenv
from os import environ

load_dotenv()


class Config(object):
    # General Config
    SECRET_KEY = os.getenv("SECRET_KEY")
    FLASK_APP = os.getenv("FLASK_APP")
    FLASK_ENV = os.getenv("FLASK_ENV")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
