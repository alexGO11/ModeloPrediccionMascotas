from sqlalchemy import Table, Column, Float, String
from config.db_connection import engine, meta_data

# Definition of the PostCode table used in the database
pc = Table("post_code", meta_data,
    Column("post_code", String(5), primary_key=True),
    Column("census", Float, nullable=False)
)

meta_data.create_all(engine)
