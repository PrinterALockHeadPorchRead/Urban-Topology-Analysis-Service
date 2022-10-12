from typing import TYPE_CHECKING, List
from sqlalchemy.engine.reflection import Inspector as _inspector

import database as _database
import models as _models
import schemas as _schemas

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

def _add_table():
    inspector = _inspector.from_engine(_database.engine)
    if not _models.City.__tablename__ in inspector.get_table_names():
        return _database.Base.metadata.create_all(bind=_database.engine)

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def create_city(city: _schemas._BaseCity, db: "Session") -> _schemas.City:
    city = _models.City(**city.dict())
    db.add(city)
    db.commit()
    db.refresh(city)
    return _schemas.City.from_orm(city)

async def get_cities(page: int, per_page: int, db: "Session") -> List[_schemas.City]:
    cities = db.query(_models.City).all()
    cities = cities[page * per_page : (page + 1) * per_page]
    return list(map(_schemas.City.from_orm, cities))

async def get_city(city_id: int, db: "Session") -> _schemas.City:
    city = db.query(_models.City).filter(_models.City.id == city_id).first()
    return city

async def get_city_by_name(city_name: str, db: "Session") -> _schemas.City:
    if city_name is None:
        return None
    city = db.query(_models.City).filter(_models.City.city_name == city_name).first()
    return city

async def get_cities_by_fields(required_city_fields: _schemas._BaseCity, db: "Session") -> List[_schemas.City]:
    query = db.query(_models.City)

    if required_city_fields.city_name != '' and not required_city_fields.city_name is None: 
        query = query.filter(_models.City.city_name == required_city_fields.city_name)
    if required_city_fields.country != '' and not required_city_fields.city_name is None:      
        query = query.filter(_models.City.country == required_city_fields.country)
    if required_city_fields.region != '' and not required_city_fields.city_name is None:      
        query = query.filter(_models.City.region == required_city_fields.region)

    return query.all()

async def delete_city(city: _models.City, db: "Session"):
    db.delete(city)
    db.commit()

async def update_city(city_data: _schemas._BaseCity, city: _models.City, db: "Session") -> _schemas.City:
    if not city_data.country is None and city_data.country != '':      
        city.country = city_data.country
    if not city_data.region is None and city_data.country != '':      
        city.region = city_data.region

    db.commit()
    db.refresh(city)

    return _schemas.City.from_orm(city)

    