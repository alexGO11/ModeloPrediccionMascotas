from sqlalchemy import Table, Column, Float, String, Integer
from config.db_connection import engine, meta_data

# Definition of the Aemet table used in the database
aemet = Table(
    "aemet",
    meta_data,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("lon", Float, nullable=False),
    Column("lat", Float, nullable=False),
    Column("date", String(10), nullable=False),
    Column("temp", Float, nullable=False),
    Column("location", String(50), nullable=False)
    )

meta_data.create_all(engine)
