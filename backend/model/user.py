from sqlalchemy import Table, Column, Float, String
from config.db_connection import engine, meta_data

pc = Table("users", meta_data,
    Column("email", primary_key=True),
    Column("name", String, nullable=False),
    Column("password", String, nullable=False)
)

meta_data.create_all(engine)
