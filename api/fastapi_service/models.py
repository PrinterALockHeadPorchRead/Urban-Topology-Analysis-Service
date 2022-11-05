from sqlalchemy import Column, Integer, Boolean, DateTime, Float
from sqlalchemy.dialects.mysql import VARCHAR
from database import Base
from datetime import datetime 

class City(Base):
    __tablename__ = "Cities"
   
    id = Column(type_=Integer, primary_key=True, autoincrement=True, nullable=True)
    id_property = Column(type_=Integer)
    city_name = Column(type_=VARCHAR(30), unique=True)
    downloaded = Column(type_=Boolean, index=True, default=False)

class CityProperty(Base):
    __tablename__ = "CityProperties"
   
    id = Column(type_=Integer, primary_key=True, autoincrement=True, nullable=True)
    id_center = Column(type_=Integer)
    id_district = Column(type_=Integer)
    id_start_polygon = Column(type_=Integer)
    population = Column(type_=Integer)
    population_density = Column(type_=Float, default=0, index=True)
    time_zone = Column(type_=VARCHAR(6))
    time_created = Column(type_=DateTime, index=True, default=datetime.utcnow)

class Point(Base):
    __tablename__ = "Points"

    id = Column(type_=Integer, primary_key=True, autoincrement=True, nullable=True)
    longitude = Column(type_=Float)
    latitude = Column(type_=Float)



