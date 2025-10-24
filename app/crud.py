from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from . import models, schemas, cache
import json
import zlib

def _serialize_record(record):
    if record is None:
        return None
    try:
        return {col.name: getattr(record, col.name) for col in record.__table__.columns}
    except Exception:
        return {k: v for k, v in record.__dict__.items() if not k.startswith('_sa_')}

def get_all_redis(db: Session, model, passenger_count: int = None, _range: int = None):
    if _range is not None:
        limit = _range
    else:
        limit = 10000

    cache_key = f"all_{model.__name__}_{limit}"
    if passenger_count is not None:
        cache_key += f"_{passenger_count}"

    cached_data = cache.get_cache(cache_key)
    if cached_data:
        try:
            decompressed = zlib.decompress(cached_data)
            return json.loads(decompressed)
        except Exception:
            pass

    query = db.query(model)
    if passenger_count is not None:
        query = query.filter(model.passenger_count == passenger_count)
    records = query.limit(limit).all()

    serialized = [_serialize_record(record) for record in records]
    try:
        compressed = zlib.compress(json.dumps(serialized, default=str).encode("utf-8"))
        cache.set_cache(cache_key, compressed)
    except Exception:
        pass

    return serialized

def get_complete_records_redis(db: Session, passenger_count: int = None, _range: int = None):
    if _range is not None:
        limit = round(_range/2)
    else:
        limit = 5000

    cache_key = f"complete_rides_{limit}"
    if passenger_count is not None:
        cache_key += f"_{passenger_count}"

    cached_data = cache.get_cache(cache_key)
    if cached_data:
        try:
            decompressed = zlib.decompress(cached_data)
            return json.loads(decompressed)
        except Exception as e:
            print(f"Cache read failed ({cache_key}): {e}")

    query1 = db.query(models.RideVendor1)
    query2 = db.query(models.RideVendor2)

    if passenger_count is not None:
        query1 = query1.filter(models.RideVendor1.passenger_count == passenger_count)
        query2 = query2.filter(models.RideVendor2.passenger_count == passenger_count)

    vendor1_rides = query1.limit(limit).all()
    vendor2_rides = query2.limit(limit).all()

    combined_rides = vendor1_rides + vendor2_rides
    sorted_rides = sorted(combined_rides, key=lambda ride: ride.id)

    serialized = [_serialize_record(ride) for ride in sorted_rides]
    try:
        compressed = zlib.compress(json.dumps(serialized, default=str).encode("utf-8"))
        cache.set_cache(cache_key, compressed)
    except Exception as e:
        print(f"Cache write failed ({cache_key}): {e}")

    return serialized

def get_by_id_redis(db: Session, model, record_id: str):
    cache_key = f"{model.__name__}_{record_id}"
    
    cached_data = cache.get_cache(cache_key)
    if cached_data:
        return json.loads(cached_data.decode("utf-8"))

    record = db.query(model).filter(model.id == record_id).first()
    
    if record:
        cache.set_cache(cache_key, json.dumps(_serialize_record(record), default=str))
    
    return record

def get_all(db: Session, model, passenger_count: int = None, _range: int = None):
    if _range is not None:
        limit = _range
    else:
        limit = 10000

    if passenger_count:
        records = db.query(model).filter(model.passenger_count == passenger_count).limit(limit).all()
        return records

    records = db.query(model).limit(limit).all()
        
    return records

def get_complete_records(db: Session, passenger_count: int = None, _range: int = None):
    if _range is not None:
        limit = round(_range/2)
    else:
        limit = 10000

    if passenger_count:
        vendor1_rides = db.query(models.RideVendor1).filter(model.passenger_count == passenger_count).limit(limit).all()
        vendor2_rides = db.query(models.RideVendor2).filter(model.passenger_count == passenger_count).limit(limit).all()
        combined_rides = vendor1_rides + vendor2_rides
        sorted_rides = sorted(combined_rides, key=lambda ride: ride.id)
        return sorted_rides

    vendor1_rides = db.query(models.RideVendor1).limit(limit).all()
    vendor2_rides = db.query(models.RideVendor2).limit(limit).all()
    
    combined_rides = vendor1_rides + vendor2_rides
    
    sorted_rides = sorted(combined_rides, key=lambda ride: ride.id)
        
    return sorted_rides

def get_by_id(db: Session, model, record_id: str):
    record = db.query(model).filter(model.id == record_id).first()
    
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
