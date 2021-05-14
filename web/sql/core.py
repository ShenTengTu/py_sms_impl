from functools import lru_cache
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session, close_all_sessions
from sqlalchemy_utils.functions import database_exists, create_database
from ..settings import get_settings


@lru_cache()
def get_engine():
    # determines driver
    settings = get_settings()
    parts = settings.sql_db_url.split("://")
    url = f"{parts[0]}+{settings.sql_db_driver}://{parts[1]}"
    return create_engine(url)


_mk_orm_session = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def init_db(metadata: MetaData):
    engine = get_engine()
    if not database_exists(engine.url):
        create_database(engine.url)
    metadata.create_all(bind=engine)


def close_db():
    close_all_sessions()
    get_engine().dispose()


def db_session():
    """FastAPI dependency genarator for create database session."""
    db: Session = _mk_orm_session()
    try:
        yield db
    finally:
        db.close()
