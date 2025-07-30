import os

class Config:
    """Base configuration.

    The data directory can be overridden with the ``VOX_DATA_DIR`` environment
    variable to allow flexible deployment locations.  If not set, it defaults to
    the ``data`` directory within the package.
    """

    DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    DATA_DIR = os.getenv('VOX_DATA_DIR', DEFAULT_DATA_DIR)
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
