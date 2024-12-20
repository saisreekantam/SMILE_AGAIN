import os

SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True

SECRET_KEY = os.urrandom(24)
