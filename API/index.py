import os
import sys
from modules.app import create_app
from modules.logger import logger

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
os.environ.update({'ROOT_PATH': ROOT_PATH})
sys.path.append(os.path.join(ROOT_PATH, 'modules'))

LOG = logger.get_root_logger(os.environ.get(
    'ROOT_LOGGER', 'root'), filename=os.path.join(ROOT_PATH, 'output.log'))

CONFIG_NAME = os.getenv('API')
if not CONFIG_NAME:
    CONFIG_NAME = "development"
API = create_app(CONFIG_NAME)

if __name__ == '__main__':
    API.run(use_reloader=False, host='0.0.0.0', port=8881)