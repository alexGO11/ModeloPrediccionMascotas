from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from .settings_env import settings

DB_DIALECT = settings.db_dialect
DB_USER = settings.db_user
DB_PASSWORD = settings.db_pass
DB_HOST = settings.db_host
DB_NAME = settings.db_name

URL_CONECTION = '{}://{}:{}@{}/{}'.format(DB_DIALECT, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

print("URL de conexión:", URL_CONECTION)

engine = create_engine(URL_CONECTION)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

meta_data = MetaData()