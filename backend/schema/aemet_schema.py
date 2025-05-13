from pydantic import BaseModel

class AemetSchema(BaseModel):
    lat: float
    lon: float
    date: str
    temp: float
    location: str
