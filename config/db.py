from sqlalchemy import create_engine, MetaData

engine = create_engine("mysql+pymysql://root:pablojeb@localhost:3306/mascotas")

meta_data = MetaData()