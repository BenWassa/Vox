import os

class Config:
    """Base configuration."""
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'INFO'

class DevConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProdConfig(Config):
    """Production configuration."""
    pass

class TestConfig(Config):
    """Configuration used during tests."""
    TESTING = True
    LOG_LEVEL = 'DEBUG'
