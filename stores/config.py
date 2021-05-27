class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:sushansujakhu14@localhost/ecommerce'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'your_email@gmail.com'
    MAIL_PASSWORD = 'your_password'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

class TestingConfig(Config):
    TESTING = True