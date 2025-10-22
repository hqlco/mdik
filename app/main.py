from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
import models, crud, schemas

app = FastAPI(title="Taxi Rides API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def register_routes(prefix: str, model):
    @app.get(f"/{prefix}")
    def get_all_records(db: Session = Depends(get_db)):
        return crud.get_all(db, model)

    @app.get(f"/{prefix}/{{record_id}}")
    def get_record(record_id: str, db: Session = Depends(get_db)):
        record = crud.get_by_id(db, model, record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        return record

    @app.post(f"/{prefix}")
    def create_record(record: schemas.RideCreate, db: Session = Depends(get_db)):
        try:
            return crud.create_record(db, model, record)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=str(e.__cause__ or e))

    @app.put(f"/{prefix}/{{record_id}}")
    def update_record(record_id: str, record: schemas.RideUpdate, db: Session = Depends(get_db)):
        try:
            return crud.update_record(db, model, record_id, record)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=str(e.__cause__ or e))

    @app.delete(f"/{prefix}/{{record_id}}")
    def delete_record(record_id: str, db: Session = Depends(get_db)):
        try:
            return crud.delete_record(db, model, record_id)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=str(e.__cause__ or e))

register_routes("rides/vendor1", models.RideVendor1)
register_routes("rides/vendor2", models.RideVendor2)

@app.get("/rides")
def get_complete_records(db: Session = Depends(get_db)):
    try:
        result = crud.get_complete_records(db)
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e.__cause__ or e))