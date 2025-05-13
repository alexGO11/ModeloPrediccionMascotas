from sqlalchemy import Table, Column, Float, String
from config.db import engine, meta_data

aemet = Table(
    "aemet",
    meta_data,
    Column("lon", Float),
    Column("lat", Float),
    Column("date", String(10)),
    Column("temp", Float),
    Column("location", String(50))
    )

meta_data.create_all(engine)
