from dataclasses import dataclass
from datetime import date, time
from typing import Optional


@dataclass
class Port:
    id: Optional[int]
    name: str
    country: Optional[str] = None
    description: Optional[str] = None


@dataclass
class CruiseDay:
    id: Optional[int]
    cruise_id: int
    day_number: int
    date: date
    port_id: Optional[int] = None
    arrival_time: Optional[time] = None
    departure_time: Optional[time] = None


@dataclass
class Cabin:
    id: Optional[int]
    cruise_id: int
    cabin_number: str
