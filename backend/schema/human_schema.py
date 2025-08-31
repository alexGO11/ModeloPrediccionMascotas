from pydantic import BaseModel
import datetime

# Scheme for human cases data
class HumanSchema(BaseModel):
    id: int
    disease: str
    date: datetime.datetime