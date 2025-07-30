from . import create_app
from .config import DevConfig, ProdConfig
import os

config_map = {
    'prod': ProdConfig,
    'dev': DevConfig,
}

env = os.getenv('VOX_ENV', 'dev')
app = create_app(config_map.get(env, DevConfig))

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
