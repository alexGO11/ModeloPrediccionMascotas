from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import  String, JSON, Integer, DateTime, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT

from config.db import engine, meta_data


precalculated = Table(
    "precalculated", meta_data,
    Column("id", Integer, primary_key=True),
    Column("disease", String(10)),
    Column("days_interval", String(5)),
    Column("end_date", DateTime),
    Column("result_data", MEDIUMTEXT)  # Use MEDIUMTEXT for larger JSON data
)

meta_data.create_all(engine)
