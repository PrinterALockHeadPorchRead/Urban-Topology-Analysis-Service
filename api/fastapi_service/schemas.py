from pydantic import BaseModel
from typing import Optional, List


class PointBase(BaseModel):
    longitude : float
    latitude : float

class PropertyBase(BaseModel):
    population : int
    population_density : Optional[float]
    center : Optional[PointBase]
    time_zone : str
    time_created : str

class CityBase(BaseModel):
    id : int 
    city_name : str 
    property : Optional[PropertyBase] 
    downloaded : Optional[bool] = False

class RegionBase(BaseModel):
    id : int
    depth : int
    name : str
    regions : List[List[List[float]]]


    

