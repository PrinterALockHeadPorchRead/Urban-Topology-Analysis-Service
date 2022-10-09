from typing import TYPE_CHECKING, List
from sqlalchemy.engine.reflection import Inspector as _inspector

import database as _database
import models as _models
import schemas as _schemas

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

def _add_table():
    inspector = _inspector.from_engine(_database.engine)
    if not _models.Car.__tablename__ in inspector.get_table_names():
        return _database.Base.metadata.create_all(bind=_database.engine)

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def create_car(car: _schemas.CreateCar, db: "Session") -> _schemas.Car:
    car = _models.Car(**car.dict())
    db.add(car)
    db.commit()
    db.refresh(car)
    return _schemas.Car.from_orm(car)

async def get_cars(page: int, per_page: int, db: "Session") -> List[_schemas.Car]:
    cars = db.query(_models.Car).all()
    cars = cars[page * per_page : (page + 1) * per_page]
    return list(map(_schemas.Car.from_orm, cars))


async def get_car(car_id: int, db: "Session") -> _schemas.Car:
    car = db.query(_models.Car).filter(_models.Car.id == car_id).first()
    return car

async def get_car_by_number(car_number: str, db: "Session") -> _schemas.Car:
    if car_number is None:
        return None
    car = db.query(_models.Car).filter(_models.Car.car_number == car_number).first()
    return car

async def get_cars_by_fields(required_car_fields: _schemas.UpdateCar, db: "Session") -> List[_schemas.Car]:
    query = db.query(_models.Car)

    if not required_car_fields.car_number is None: 
        query = query.filter(_models.Car.car_number == required_car_fields.car_number)
    if not required_car_fields.model is None:      
        query = query.filter(_models.Car.model == required_car_fields.model)
    if not required_car_fields.owner is None:      
        query = query.filter(_models.Car.owner == required_car_fields.owner)
    if not required_car_fields.odometer is None:   
        query = query.filter(_models.Car.odometer == required_car_fields.odometer)

    return query.all()

async def delete_car(car: _models.Car, db: "Session"):
    db.delete(car)
    db.commit()

async def update_car(car_data: _schemas.CreateCar, car: _models.Car, db: "Session") -> _schemas.Car:
    car.car_number = car_data.car_number
    if not car_data.model is None:      car.model = car_data.model
    if not car_data.owner is None:      car.owner = car_data.owner
    if not car_data.odometer is None:   car.odometer = car_data.odometer
    if not car_data.picture is None:    car.picture = car_data.picture

    db.commit()
    db.refresh(car)

    return _schemas.Car.from_orm(car)

async def update_car(car_data: _schemas.UpdateCar, car: _models.Car, db: "Session") -> _schemas.Car:
    if not car_data.car_number is None: car.car_number = car_data.car_number
    if not car_data.model is None:      car.model = car_data.model
    if not car_data.owner is None:      car.owner = car_data.owner
    if not car_data.odometer is None:   car.odometer = car_data.odometer
    if not car_data.picture is None:    car.picture = car_data.picture

    db.commit()
    db.refresh(car)

    return _schemas.Car.from_orm(car)
    