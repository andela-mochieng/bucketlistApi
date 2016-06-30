import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True


class DevConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'dev.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'test.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(Config):
    """Production configurations."""

    DEBUG = False
    DATABASE_URI = 'sqlite:///bucketlist.db'

config = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'SECRET_KEY': 'RAINSECRETKEY'
}
