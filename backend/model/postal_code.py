from sqlalchemy import Table, Column, Float, String
from config.db import engine, meta_data

pc = Table(
    "post_codes",
    meta_data,
    Column("post_code", String(5), primary_key=True),
    Column("census", Float, nullable=False)
)

meta_data.create_all(engine)
