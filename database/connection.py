# database/connection.py
import json
import mysql.connector
from mysql.connector import Error

with open("database/config.json", "r") as config_file:
    config = json.load(config_file)

class DatabaseConnection:
    def __init__(self):
        self.host = config["database"]["host"]
        self.user = config["database"]["user"]
        self.password = config["database"]["password"]
        self.database = config["database"]["name"]
        self.connection = None

    def __enter__(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Conexión a la base de datos establecida.")
            return self.connection
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
            print("Conexión a la base de datos cerrada.")