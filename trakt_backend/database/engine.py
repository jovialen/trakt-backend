import sqlite3

from sqlalchemy import Engine, create_engine, event


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
    if not isinstance(dbapi_connection, sqlite3.Connection):
        return

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_secure_engine(connection_url: str, token: str | None):
    connect_args = (
        {"check_same_thread": False, "auth_token": token}
        if token is not None and token != ""
        else {"check_same_thread": False}
    )
    return create_engine(connection_url, connect_args=connect_args)
