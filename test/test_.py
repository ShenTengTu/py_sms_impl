# This file must be the first order of testing
import os
from web.settings import get_settings
from web.crypto import crypt_context, crypt_hash, crypt_verify
from web.sql.orm import dump_schema, orm_metadata


def test_setting():
    settings = get_settings()
    assert settings.secret_key.get_secret_value() == "test_secret_key"
    assert settings.csrf_secret_key.get_secret_value() == "test_csrf_secret_key"
    assert settings.max_age == 600
    assert settings.sql_db_url.scheme == "postgresql"
    assert settings.sql_db_url.user == "postgres"
    assert settings.sql_db_url.password == os.environ["SQL_DB_PASSWORD"]
    assert settings.sql_db_url.host == os.environ["SQL_DB_HOST"]
    assert settings.sql_db_url.port == "5432"
    assert settings.sql_db_url.path == "/%s" % os.environ["SQL_DB_NAME"]


def test_crypt():
    assert id(crypt_context()) == id(crypt_context())
    p = "test_secret"
    assert crypt_verify(p, crypt_hash(p))
    assert not crypt_verify(p.capitalize(), crypt_hash(p))


def test_sql_dump_schema():
    assert dump_schema().count("CREATE TABLE") > 0


def test_sql_init_db():
    from sqlalchemy import inspect
    from sqlalchemy_utils import database_exists, drop_database
    from web.sql.core import init_db, get_engine

    url = get_settings().sql_db_url
    metadata = orm_metadata()
    init_db(metadata)

    assert database_exists(url)
    for t in metadata.tables.values():
        assert inspect(get_engine()).has_table(t.name)

    init_db(metadata)  # should not raise error

    drop_database(url)
