from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Date, Boolean
from config.db_connection import engine, meta_data

# Definition of the Tests table used in the database
tests = Table("test", meta_data, 
             Column("id_test", Integer, primary_key=True),
             Column("post_code", String(5), nullable=False),
             Column("date_done", Date,  nullable=False),
             Column("disease", String(50),  nullable=False),
             Column("result", Integer,  nullable=False),
             Column("city", String(50)),
             Column("age", Integer),
             Column("sex", String(50)))

meta_data.create_all(engine)
