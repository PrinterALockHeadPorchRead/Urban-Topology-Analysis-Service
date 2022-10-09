import datetime as _dt
from email.policy import default
from tkinter import NO
import sqlalchemy as _sql
import database as _database

class Car(_database.Base):
    __tablename__="car"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)

    car_number = _sql.Column(_sql.VARCHAR(10), unique=True)
    model = _sql.Column(_sql.VARCHAR(30))
    owner = _sql.Column(_sql.VARCHAR(10))
    odometer = _sql.Column(_sql.REAL)
    picture = _sql.Column(_sql.String)

