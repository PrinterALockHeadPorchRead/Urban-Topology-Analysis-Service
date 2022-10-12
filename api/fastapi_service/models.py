import datetime as _dt
import sqlalchemy as _sql
import database as _database

class City(_database.Base):
    __tablename__="city"
   
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)

    country = _sql.Column(_sql.VARCHAR(30), default='')
    region = _sql.Column(_sql.VARCHAR(30), default='')
    city_name = _sql.Column(_sql.VARCHAR(30), unique=True)

