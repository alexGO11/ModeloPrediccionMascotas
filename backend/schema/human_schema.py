from pydantic import BaseModel
import datetime

class HumanSchema(BaseModel):
    id: int
    disease: str
    date: datetime.datetime