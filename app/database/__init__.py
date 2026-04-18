from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

def get_engine(database_url: str = SQLALCHEMY_DATABASE_URL):

    # Factory function to create a new SQLAlchemy engine.

    return create_engine(database_url)
