from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from .settings_env import settings

# Load database configuration from environment settings
DB_DIALECT = settings.db_dialect
DB_USER = settings.db_user
DB_PASSWORD = settings.db_pass
DB_HOST = settings.db_host
DB_NAME = settings.db_name

# Construct the database connection URL
URL_CONNECTION = '{}://{}:{}@{}/{}'.format(DB_DIALECT, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

print("DB_CONNECTION| URL de conexión:", URL_CONNECTION)

# Create the SQLAlchemy engine for database interactions
engine = create_engine(URL_CONNECTION)

# Create a new session local class and initialize Metadata
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

meta_data = MetaData()