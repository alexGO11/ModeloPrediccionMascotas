from pydantic import BaseModel

# Scheme for census data by postal code
class PostalCodeSchema(BaseModel):
    post_code: str
    census: float
