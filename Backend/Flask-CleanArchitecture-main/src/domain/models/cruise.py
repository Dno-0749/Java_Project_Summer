from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Cruise:
    id: Optional[int]
    name: str
    start_date: date
    end_date: date
    status: str = "planned"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
