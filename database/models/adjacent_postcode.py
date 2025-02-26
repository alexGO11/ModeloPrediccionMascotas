# database/models/adjacent_postcode.py
class AdjacentPostcode:
    def __init__(self, post_code_origin, post_code_adjacent):
        self.post_code_origin = post_code_origin
        self.post_code_adjacent = post_code_adjacent

    def __repr__(self):
        return f"AdjacentPostcode(post_code_origin={self.post_code_origin}, post_code_adjacent={self.post_code_adjacent})"