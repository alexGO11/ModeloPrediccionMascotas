from pydantic import BaseModel

class PostalCodeSchema(BaseModel):
    post_code: str
    z_value_3m: float
    z_value_9m: float
    z_value_1y: float
    z_value_2y: float