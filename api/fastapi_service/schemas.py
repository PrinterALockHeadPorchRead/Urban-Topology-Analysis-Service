from tkinter.messagebox import NO
from typing import Optional
import pydantic as _pydantic

class _BaseCar(_pydantic.BaseModel):
    car_number : str
    model : Optional[str] = None
    owner : Optional[str] = None
    odometer : Optional[float] = None
    picture : Optional[str] = None

class Car(_BaseCar):
    id : int
    class Config:
        orm_mode = True
    
class CreateCar(_BaseCar):
    def to_str(self):
        return ("{ " + f"car_number : {self.car_number}, "
                f"model : {self.model}, "
                f"owner : {self.owner}, "
                f"odometer : {self.odometer}, "
                f"picture : {self.picture}" + " }")
    pass 

class UpdateCar(_pydantic.BaseModel):
    id : int
    car_number : Optional[str] = None
    model : Optional[str] = None
    owner : Optional[str] = None
    odometer : Optional[float] = None
    picture : Optional[str] = None

    def to_str(self):
          return ("{ " + f"id : {self.id}, "
                  f"car_number : {self.car_number}, "
                  f"model : {self.model}, "
                  f"owner : {self.owner}, "
                  f"odometer : {self.odometer}, "
                  f"picture : {self.picture}" + " }")


class GetCar(_pydantic.BaseModel):
    id : Optional[int] = None
    car_number : Optional[str] = None
    model : Optional[str] = None
    owner : Optional[str] = None
    odometer : Optional[float] = None
    picture : Optional[str] = None

    def to_str(self):
          return ("{ " + f"id : {self.id}, "
                  f"car_number : {self.car_number}, "
                  f"model : {self.model}, "
                  f"owner : {self.owner}, "
                  f"odometer : {self.odometer}, "
                  f"picture : {self.picture}" + " }")