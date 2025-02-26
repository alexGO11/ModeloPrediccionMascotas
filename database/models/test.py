# database/models/test.py
class Test:
    def __init__(self, id_test, post_code, date_done, disease, result, city=None, age=None, sex=None):
        self.id_test = id_test
        self.post_code = post_code
        self.date_done = date_done
        self.disease = disease
        self.result = result
        self.city = city
        self.age = age
        self.sex = sex

    def __repr__(self):
        return f"Test(id_test={self.id_test}, post_code={self.post_code}, date_done={self.date_done}, disease={self.disease}, result={self.result})"