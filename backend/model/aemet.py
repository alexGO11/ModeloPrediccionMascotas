from sqlalchemy import Table, Column, Float, String
from config.db_connection import engine, meta_data

aemet = Table(
    "aemet",
    meta_data,
    Column("id", String(10), primary_key=True),
    Column("lon", Float, nullable=False),
    Column("lat", Float, nullable=False),
    Column("date", String(10), nullable=False),
    Column("temp", Float, nullable=False),
    Column("location", String(50), nullable=False)
    )

meta_data.create_all(engine)
