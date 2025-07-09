from pydantic import BaseModel
from typing import Dict, Any
import datetime

class PrecalculatedSchema(BaseModel):
    id: int
    disease: str
    days_interval: str
    end_date: datetime.datetime
    result_data: str
    
