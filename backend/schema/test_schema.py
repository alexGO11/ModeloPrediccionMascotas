from pydantic import BaseModel
from typing import Optional
import datetime

class TestSchema(BaseModel):
    id_test: Optional[int] = None  
    post_code: str
    date_done: datetime.datetime
    desease: str
    result: int
    city: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
