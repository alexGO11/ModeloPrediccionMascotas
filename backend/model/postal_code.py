from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, Float
from config.db import engine, meta_data


pc = Table("postal_codes", meta_data, 
             Column("post_code", Integer, primary_key=True),
             Column("censo", Float, nullable=False)
            )

meta_data.create_all(engine)