from pydantic import BaseModel

class PostalCodeSchema(BaseModel):
    post_code: str
    census: float
