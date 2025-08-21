from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import  String, JSON, Integer, DateTime, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT

from config.db_connection import engine, meta_data

precalculated = Table(
    "precalculated", meta_data,
    Column("id", String(10), primary_key=True),
    Column("disease", String(15), nullable=False),
    Column("days_interval", Integer, nullable=False),
    Column("end_date", DateTime, nullable=False),
    Column("result_data", MEDIUMTEXT, nullable=False)  # Use MEDIUMTEXT for larger JSON data
)

meta_data.create_all(engine)
