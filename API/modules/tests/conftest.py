import os
import sys
import tempfile

import pytest

from modules.app import create_app
from modules.logger import logger

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
os.environ.update({'ROOT_PATH': ROOT_PATH})
sys.path.append(os.path.join(ROOT_PATH, 'modules'))

LOG = logger.get_root_logger(os.environ.get(
    'ROOT_LOGGER', 'root'), filename=os.path.join(ROOT_PATH, 'output.log'))

@pytest.fixture(scope="session")
def client():
    """init app for testing"""
    test_db_fd, test_db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'MONGO_URI': 'mongodb://127.0.0.1:27017/MyBookingServices',
        'JWT_SECRET_KEY': 'SeCretPasSword9'
    })

    print(test_db_path)
    clt = app.test_client()
    yield clt
    os.close(test_db_fd)
