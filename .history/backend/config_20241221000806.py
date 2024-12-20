import os

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Secret key
SECRET_KEY = os.urrandom(24)
