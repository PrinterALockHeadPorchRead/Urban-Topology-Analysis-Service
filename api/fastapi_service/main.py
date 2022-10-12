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

@app.get("/api/city/{city_id}/", response_model=_schemas.City)
@logger.catch(exclude=_fastapi.HTTPException)
async def get_city(
    city_id: int, 
    db:_orm.Session = _fastapi.Depends(_services.get_db)
):
    request = f"GET /api/city/{city_id}/"
    status_code = 200
    detail = "OK"

    city = await _services.get_city(city_id=city_id, db=db)
    if city is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise _fastapi.HTTPException(status_code=status_code, detail=detail)
    
    logger.info(f"{request} {status_code} {detail}")
    return city

@app.get("/api/city/", response_model=List[_schemas.City])
@logger.catch(exclude=_fastapi.HTTPException)
async def get_cities(
    page: int, 
    per_page : int,
    db:_orm.Session = _fastapi.Depends(_services.get_db)
):
    request = f"GET /api/city/?page={page}&per_page={per_page}/"
    status_code = 200
    detail = "OK"

    if page < 0 or per_page <= 0:
        status_code = 400
        detail = "BAD REQUEST"
        logger.error(f"{request} {status_code} {detail}")
        raise _fastapi.HTTPException(status_code=status_code, detail=detail)
    
    cities = await _services.get_cities(page=page, per_page=per_page, db=db)  

    logger.info(f"{request} {status_code} {detail}")
    return cities

@app.post("/api/cities", response_model=List[_schemas.City])
@logger.catch(exclude=_fastapi.HTTPException)
async def get_cities_by_fields(
    required_city_fields: _schemas._BaseCity,
    db:_orm.Session = _fastapi.Depends(_services.get_db)
):
    request = f"GET /api/cities/ {required_city_fields.to_str()}"
    status_code = 200
    detail = "OK"

    cities = await _services.get_cities_by_fields(required_city_fields=required_city_fields, db=db)
    if cities is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise _fastapi.HTTPException(status_code=status_code, detail=detail)
    
    logger.info(f"{request} {status_code} {detail}")
    return cities


@app.post("/api/city/", response_model=_schemas.City)
@logger.catch(exclude=_fastapi.HTTPException)
async def create_city(
    city_info: _schemas._BaseCity, 
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    request = f"POST /api/city/ {city_info.to_str()}"
    status_code = 200
    detail = "OK"

    city = await _services.get_city_by_name(db=db, city_name=city_info.city_name)
    if city is None:
        city = await _services.create_city(city=city_info, db=db)
    else:
        city = await _services.update_city(city_data=city_info, city=city, db=db)
        
    logger.info(f"{request} {status_code} {detail}")
    return city


@app.delete("/api/city/{city_id}/")
@logger.catch(exclude=_fastapi.HTTPException)
async def delete_city(
    city_id: int, 
    db:_orm.Session = _fastapi.Depends(_services.get_db)
):
    request = f"DELETE /api/city/{city_id}/"
    status_code = 200
    detail = "OK"

    city = await _services.get_city(db=db, city_id=city_id)
    if city is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise _fastapi.HTTPException(status_code=status_code, detail=detail)

    await _services.delete_city(city, db=db)

    logger.info(f"{request} {status_code} {detail}")
    return f"{status_code} {detail}"

if __name__ == "__main__":
    _services._add_table()
    _uvicorn.run("main:app", host="0.0.0.0", port=_os.getenv("PORT", 8002))