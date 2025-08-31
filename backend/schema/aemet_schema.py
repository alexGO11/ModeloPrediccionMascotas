from pydantic import BaseModel

# Scheme for Aemet data
class AemetSchema(BaseModel):
    lat: float
    lon: float
    date: str
    temp: float
    location: str
