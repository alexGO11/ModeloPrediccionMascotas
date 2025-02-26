# database/models/post_code.py
class PostCode:
    def __init__(self, post_code, n_cases=0, estimation_pets=0.0):
        self.post_code = post_code
        self.n_cases = n_cases
        self.estimation_pets = estimation_pets

    def __repr__(self):
        return f"PostCode(post_code={self.post_code}, n_cases={self.n_cases}, estimation_pets={self.estimation_pets})"