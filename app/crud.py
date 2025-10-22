from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import models, schemas
import cache
import json

def _serialize_record(record):
    if record is None:
        return None
    try:
        return {col.name: getattr(record, col.name) for col in record.__table__.columns}
    except Exception:
        return {k: v for k, v in record.__dict__.items() if not k.startswith('_sa_')}


def get_all(db: Session, model):
    cache_key = f"all_{model.__name__}"
    
    cached_data = cache.get_cache(cache_key)
    if cached_data:
        return json.loads(cached_data)

    records = db.query(model).all()
    
    cache.set_cache(cache_key, json.dumps([_serialize_record(record) for record in records], default=str))
    
    return records

def get_complete_records(db: Session):
    limit = 10
    cache_key = f"complete_rides_{limit}"
    
    cached_data = cache.get_cache(cache_key)
    if cached_data:
        return json.loads(cached_data)

    vendor1_rides = db.query(models.RideVendor1).limit(limit).all()
    vendor2_rides = db.query(models.RideVendor2).limit(limit).all()
    
    combined_rides = vendor1_rides + vendor2_rides
    
    sorted_rides = sorted(combined_rides, key=lambda ride: ride.id)
    
    cache.set_cache(cache_key, json.dumps([_serialize_record(ride) for ride in sorted_rides], default=str))
    
    return sorted_rides

def get_by_id(db: Session, model, record_id: str):
    cache_key = f"{model.__name__}_{record_id}"
    
    cached_data = cache.get_cache(cache_key)
    if cached_data:
        return json.loads(cached_data)

    record = db.query(model).filter(model.id == record_id).first()
    
    if record:
        cache.set_cache(cache_key, json.dumps(_serialize_record(record), default=str))
    
    return record

def create_record(db: Session, model, record: schemas.RideCreate):
    try:
        db_record = model(**record.dict())
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def update_record(db: Session, model, record_id: str, record: schemas.RideUpdate):
    try:
        db.query(model).filter(model.id == record_id).update(record.dict(exclude_unset=True))
        db.commit()
        return {"message": "Record updated"}
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def delete_record(db: Session, model, record_id: str):
    try:
        db.query(model).filter(model.id == record_id).delete()
        db.commit()
        return {"message": "Record deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        raise e
