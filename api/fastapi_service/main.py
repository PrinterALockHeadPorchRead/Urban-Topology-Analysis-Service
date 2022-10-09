from typing import TYPE_CHECKING, List
from fastapi.middleware.cors import CORSMiddleware as _cors

import fastapi as _fastapi
import uvicorn as _uvicorn
import sqlalchemy.orm as _orm
import os as _os
import schemas as _schemas
import services as _services
import logs as _logs 

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

app = _fastapi.FastAPI()
logger = _logs.init()

app.add_middleware(
    _cors,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/car/{car_id}/", response_model=_schemas.Car)
@logger.catch(exclude=_fastapi.HTTPException)
async def get_car(
    car_id: int, 
    db:_orm.Session = _fastapi.Depends(_services.get_db)
):
    request = f"GET /api/car/{car_id}/"
    status_code = 200
    detail = "OK"

    car = await _services.get_car(car_id=car_id, db=db)
    if car is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise _fastapi.HTTPException(status_code=status_code, detail=detail)
    
    logger.info(f"{request} {status_code} {detail}")
    return car


@app.post("/api/cars", response_model=List[_schemas.Car])
@logger.catch(exclude=_fastapi.HTTPException)
async def get_cars_by_fields(
    required_car_fields: _schemas.GetCar,
    db:_orm.Session = _fastapi.Depends(_services.get_db)
):
    request = f"GET /api/car/ {required_car_fields.to_str()}"
    status_code = 200
    detail = "OK"

    cars = await _services.get_cars_by_fields(required_car_fields=required_car_fields, db=db)
    if cars is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise _fastapi.HTTPException(status_code=status_code, detail=detail)
    
    logger.info(f"{request} {status_code} {detail}")
    return cars



@app.get("/api/car/", response_model=List[_schemas.Car])
@logger.catch(exclude=_fastapi.HTTPException)
async def get_cars(
    page: int, 
    per_page : int,
    db:_orm.Session = _fastapi.Depends(_services.get_db)
):
    request = f"GET /api/car/?page={page}&per_page={per_page}/"
    status_code = 200
    detail = "OK"

    if page < 0 or per_page <= 0:
        status_code = 400
        detail = "BAD REQUEST"
        logger.error(f"{request} {status_code} {detail}")
        raise _fastapi.HTTPException(status_code=status_code, detail=detail)
    
    cars = await _services.get_cars(page=page, per_page=per_page, db=db)  

    logger.info(f"{request} {status_code} {detail}")
    return cars


@app.post("/api/car/", response_model=_schemas.Car)
@logger.catch(exclude=_fastapi.HTTPException)
async def create_car(
    car_data: _schemas.CreateCar, 
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    request = f"POST /api/car/ {car_data.to_str()}"
    status_code = 200
    detail = "OK"

    car = await _services.get_car_by_number(db=db, car_number=car_data.car_number)
    if car is None:
        car = await _services.create_car(car=car_data, db=db)
    else:
        car = await _services.update_car(car_data=car_data, car=car, db=db)
        
    logger.info(f"{request} {status_code} {detail}")
    return car


@app.delete("/api/car/{car_id}/")
@logger.catch(exclude=_fastapi.HTTPException)
async def delete_car(
    car_id: int, 
    db:_orm.Session = _fastapi.Depends(_services.get_db)
):
    request = f"DELETE /api/car/{car_id}/"
    status_code = 200
    detail = "OK"

    car = await _services.get_car(db=db, car_id=car_id)
    if car is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise _fastapi.HTTPException(status_code=status_code, detail=detail)

    await _services.delete_car(car, db=db)

    logger.info(f"{request} {status_code} {detail}")
    return f"{status_code} {detail}"


@app.put("/api/car/", response_model=_schemas.Car)
@logger.catch(exclude=_fastapi.HTTPException)
async def update_car(
    car_data: _schemas.UpdateCar,
    db:_orm.Session = _fastapi.Depends(_services.get_db),
):
    request = "UPDATE /api/car/" + car_data.to_str()
    status_code = 200
    detail = "OK"
    
    car = await _services.get_car(db=db, car_id=car_data.id)
    if car is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise _fastapi.HTTPException(status_code=status_code, detail=detail)

    car_with_the_same_number = await _services.get_car_by_number(car_number=car_data.car_number, db=db)
    if not car_with_the_same_number is None and car_with_the_same_number.id != car_data.id: 
        status_code = 409
        detail = "CAR WITH SUCH NUMBER ALREADY EXISTS"
        logger.error(f"{request} {status_code} {detail}")
        raise _fastapi.HTTPException(status_code=status_code, detail=detail)
    
    car = await _services.update_car(car_data=car_data, car=car, db=db)
    logger.info(f"{request} {status_code} {detail}")
    return car


if __name__ == "__main__":
    _services._add_table()
    _uvicorn.run("main:app", host="0.0.0.0", port=_os.getenv("PORT", 8002))