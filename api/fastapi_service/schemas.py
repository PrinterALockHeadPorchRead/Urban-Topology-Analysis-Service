from typing import Optional
import pydantic as _pydantic

class _BaseCity(_pydantic.BaseModel):
    country : Optional[str] = ''
    region : Optional[str] = ''
    city_name : str
    
    def to_str(self):
        return ("{ " + 
                f"city_name : {self.city_name}, " +
                f"country : {self.country}, " +
                f"region : {self.region}" +
                " }")

class City(_BaseCity):
    id : int

    class Config:
        orm_mode = True

    def to_str(self):
        return ("{ " + 
                f"city_id : {self.id}, " +
                f"city_name : {self.city_name}, " +
                f"country : {self.country}, " +
                f"region : {self.region}" +
                " }")