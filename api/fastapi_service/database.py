from sqlalchemy import(
    Column,
    Integer,
    VARCHAR,
    Boolean,
    Float,
    DateTime
)
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from databases import Database


DATABASE_URL = "postgresql://user:password@postgres:5432/fastapi_database"

metadata = MetaData()

CityAsync = Table(
    "Cities",
    metadata,
    Column("id", Integer, primary_key = True, autoincrement=True, nullable=True),
    Column("id_property", Integer),
    Column("city_name", VARCHAR(30), unique=True),
    Column("downloaded", Boolean, index=True, default=False)
)


CityPropertyAsync = Table(
    "CityProperties",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=True),
    Column("id_center", Integer),
    Column("id_district", Integer),
    Column("id_start_polygon"),
    Column("population", Integer),
    Column("population_density", Float, default=0, index=True),
    Column("time_zone", VARCHAR(6)),
    Column("time_created", DateTime, index=True, default=datetime.utcnow),
)


PointAsync = Table(
    "Points",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, nullable=True),
    Column("longitude", Float),
    Column("latitude", Float),
)

engine = create_engine(DATABASE_URL, echo=False)

database = Database(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()