from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Date, Boolean
from config.db import engine, meta_data


getis_ord = Table("getisord_t", meta_data, 
             Column("post_code", String(5), primary_key=True),
             Column("z_value_3m", Integer, nullable=False),
             Column("z_value_9m", Integer, nullable=False),
             Column("z_value_1y", Integer, nullable=False),
             Column("z_value_2y", Integer, nullable=False)
)

meta_data.create_all(engine)
