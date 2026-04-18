'''
TODO: I was trying to fix a pytest error for the models and thought I had to initialize DB, but I actually don't.
Re-add this when DB/other appropriate tests are added.
'''

'''
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.database import Base
from app.database import get_engine

def init_db(engine: Engine) -> None:

    Base.metadata.create_all(bind=engine)

def drop_db(engine: Engine) -> None:

    Base.metadata.drop_all(bind=engine)

if __name__ == '__main__':

    # no cover is specified in the example code, which makes sense as this is a main method

    engine = get_engine() # pragma: no cover
    drop_db(engine=engine) # pragma: no cover
    init_db(engine=engine) # pragma: no cover
'''
