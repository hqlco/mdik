from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RideBase(BaseModel):
    id: str
    vendor_id: int
    pickup_datetime: datetime
    dropoff_datetime: datetime
    passenger_count: int
    pickup_longitude: float
    pickup_latitude: float
    dropoff_longitude: float
    dropoff_latitude: float
    store_and_fwd_flag: str
    trip_duration: int

class RideCreate(RideBase):
    pass

class RideUpdate(BaseModel):
    passenger_count: Optional[int]
    pickup_longitude: Optional[float]
    pickup_latitude: Optional[float]
    dropoff_longitude: Optional[float]
    dropoff_latitude: Optional[float]
    store_and_fwd_flag: Optional[str]
    trip_duration: Optional[int]
