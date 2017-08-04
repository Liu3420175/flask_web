import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:liulh3420175@localhost:3306/test1'

    # Redis & Celery Development
    REDIS_URL = "redis://127.0.0.1:6379/2"
    CELERY_BROKER = "redis://127.0.0.1:6379/3"


class TestingConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:liulh3420175@localhost:3306/test1'

    # Redis & Celery Development
    REDIS_URL = "redis://127.0.0.1:6379/2"
    CELERY_BROKER = "redis://127.0.0.1:6379/3"

class ProductionConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:liulh3420175@localhost:3306/test1'

    # Redis & Celery Development
    REDIS_URL = "redis://127.0.0.1:6379/2"
    CELERY_BROKER = "redis://127.0.0.1:6379/3"


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


