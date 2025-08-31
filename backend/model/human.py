from sqlalchemy import Table, Column, Float, String
from sqlalchemy.sql.sqltypes import String, Date

from config.db_connection import engine, meta_data

# Definition of the Human table used in the database
human = Table(
    "human",
    meta_data,
    Column("id", String(10), primary_key=True),
    Column("post_code", String(5), nullable=False),
    Column("disease", String(20), nullable=False),
    Column("date", Date,  nullable=False)
    )

meta_data.create_all(engine)