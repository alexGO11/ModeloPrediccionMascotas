# database/services/database_service.py
from ..connection import DatabaseConnection
from ..queries import PostCodeQueries, AdjacentPostcodeQueries, TestQueries
from ..models.post_code import PostCode
from ..models.adjacent_postcode import AdjacentPostcode
from ..models.test import Test

class DatabaseService:
    def insert_post_code(self, post_code):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(PostCodeQueries.INSERT, (
                post_code.post_code,
                post_code.n_cases,
                post_code.estimation_pets
            ))
            conn.commit()

    def get_all_post_codes(self):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(PostCodeQueries.SELECT_ALL)
            return [PostCode(*row) for row in cursor.fetchall()]

    # Métodos similares para las otras tablas...