from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Activity:
    id: Optional[int]
    cruise_id: int
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    capacity: Optional[int] = None
    fee: Decimal = 0
    is_included_in_package: bool = False


@dataclass
class ShoreExcursion:
    id: Optional[int]
    cruise_day_id: int
    name: str
    provider_name: Optional[str] = None
    gathering_time: Optional[datetime] = None
    return_time: Optional[datetime] = None
    capacity: Optional[int] = None
    price: Decimal = 0
    status: str = "scheduled"


@dataclass
class Registration:
    id: Optional[int]
    passenger_id: int
    activity_id: Optional[int] = None
    excursion_id: Optional[int] = None
    status: str = "registered"
    registered_at: Optional[datetime] = None
