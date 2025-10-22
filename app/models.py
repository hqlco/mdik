from sqlalchemy import Column, String, Integer, Float, DateTime
from .database import Base

class RideVendor1(Base):
    __tablename__ = "rides_vendor1"

    id = Column(String, primary_key=True, index=True)
    vendor_id = Column(Integer)
    pickup_datetime = Column(DateTime)
    dropoff_datetime = Column(DateTime)
    passenger_count = Column(Integer)
    pickup_longitude = Column(Float)
    pickup_latitude = Column(Float)
    dropoff_longitude = Column(Float)
    dropoff_latitude = Column(Float)
    store_and_fwd_flag = Column(String)
    trip_duration = Column(Integer)


class RideVendor2(Base):
    __tablename__ = "rides_vendor2"

    id = Column(String, primary_key=True, index=True)
    vendor_id = Column(Integer)
    pickup_datetime = Column(DateTime)
    dropoff_datetime = Column(DateTime)
    passenger_count = Column(Integer)
    pickup_longitude = Column(Float)
    pickup_latitude = Column(Float)
    dropoff_longitude = Column(Float)
    dropoff_latitude = Column(Float)
    store_and_fwd_flag = Column(String)
    trip_duration = Column(Integer)
