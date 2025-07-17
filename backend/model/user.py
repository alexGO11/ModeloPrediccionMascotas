from sqlalchemy import Table, Column, Boolean, String
from config.db_connection import engine, meta_data

users = Table(
    "users", meta_data,
    Column("username", String(50), primary_key=True, nullable=False),
    Column("email", String(100), unique=True, nullable=False),
    Column("full_name", String(100)),
    Column("hashed_password", String(255), nullable=False),
    Column("disabled", Boolean, default=False),
)

meta_data.create_all(engine)
