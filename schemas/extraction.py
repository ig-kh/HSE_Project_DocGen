from pydantic import BaseModel
from typing import List, Optional


class Cost(BaseModel):
    amount: float
    currency: str
    vat: Optional[str]


class ExtractedContract(BaseModel):
    date: Optional[str]
    city: Optional[str]
    counterparty: Optional[str]
    work: Optional[str]
    work_time_days: Optional[int]
    cost: Optional[Cost]
    missing_fields: List[str]
