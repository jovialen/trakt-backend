from sqlalchemy import Engine, create_engine, event


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_database_engine(connection_url: str):
    connect_args = {"check_same_thread": False}
    return create_engine(connection_url, connect_args=connect_args)
