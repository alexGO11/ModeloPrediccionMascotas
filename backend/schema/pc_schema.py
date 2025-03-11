from pydantic import BaseModel

class PostalCodeSchema(BaseModel):
    post_code: int
    censo: float
