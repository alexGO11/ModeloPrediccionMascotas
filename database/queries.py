# database/queries.py
class PostCodeQueries:
    INSERT = """
    INSERT INTO post_code (post_code, n_cases, estimation_pets)
    VALUES (%s, %s, %s);
    """

    SELECT_ALL = "SELECT * FROM post_code;"

class AdjacentPostcodeQueries:
    INSERT = """
    INSERT INTO adjacent_postcode (post_code_origin, post_code_adjacent)
    VALUES (%s, %s);
    """

    SELECT_ALL = "SELECT * FROM adjacent_postcode;"

class TestQueries:
    INSERT = """
    INSERT INTO test (post_code, date_done, disease, result, city, age, sex)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    SELECT_ALL = "SELECT * FROM test;"