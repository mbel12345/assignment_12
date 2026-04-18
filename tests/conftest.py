import logging
import pytest

from app.core.config import settings
from app.database import get_engine
'''
TODO: I was trying to fix a pytest error for the models and thought I had to initialize DB, but I actually don't.
Re-add this when DB/other appropriate tests are added.
'''
'''
from app.database.database_init import drop_db
from app.database.database_init import init_db
'''

test_engine = get_engine(database_url=settings.DATABASE_URL)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

test_engine = get_engine(database_url=settings.DATABASE_URL)

'''
TODO: I was trying to fix a pytest error for the models and thought I had to initialize DB, but I actually don't.
Add this fixture when DB/other appropriate tests are added
'''
# @pytest.fixture(scope='session', autouse=True)
def setup_test_database(request):

    # Set up the test database before the session starts

    logger.info('Setting up test database...')

    try:
        drop_db(test_engine)
        init_db(test_engine)
        logger.info('Test database initialized')
    except Exception as e:
        logger.info(f'Error setting up test database: {str(e)}')

    yield

    if not request.config.getoption('--preserve-db'):
        logger.info('Dropping test database tables...')
        drop_db(test_engine)

def pytest_addoption(parser):

    '''
    Add custom command line options:
      --preserve-db : Keep test database after tests
      --run-slow     : Run tests marked as 'slow'
    '''

    parser.addoption('--preserve-db', action='store_true', help='Keep test database after tests')
    parser.addoption('--run-slow', action='store_true', help='Run tests marked as slow')

def pytest_collection_modifyitems(config, items):

    # Skip tests marked as 'slow' unless --run-slow is given

    if not config.getoption('--run-slow'):
        skip_slow = pytest.mark.skip(reason='use --run-slow to run')
        for item in items:
            if 'slow' in item.keywords:
                item.add_marker(skip_slow)
