from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from uvicorn import run
from os import getenv
from schemas import CityBase, RegionBase

import geopandas as gpd
import services
import logs 

regions_df = gpd.read_file('./data/regions.json', driver='GeoJSON')
app = FastAPI()
logger = logs.init()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4200", "http://localhost:8002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    services.add_tables() 
    services.init_db()
    run("main:app", host="0.0.0.0", port=getenv("PORT", 8002))

@app.get("/api/city/", response_model=CityBase)
@logger.catch(exclude=HTTPException)
async def get_city(
    city_id: int
):
    request = f"GET /api/city?city_id={city_id}"
    status_code = 200
    detail = "OK"

    city = await services.get_city(city_id=city_id)
    if city is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise HTTPException(status_code=status_code, detail=detail)
    
    logger.info(f"{request} {status_code} {detail}")
    return city

@app.get("/api/cities/", response_model=List[CityBase])
@logger.catch(exclude=HTTPException)
async def get_cities(
    page: int, 
    per_page : int
): 
    request = f"GET /api/cities?page={page}&per_page={per_page}/"
    status_code = 200
    detail = "OK"

    if page < 0 or per_page <= 0:
        status_code = 400
        detail = "BAD REQUEST"
        logger.error(f"{request} {status_code} {detail}")
        raise HTTPException(status_code=status_code, detail=detail)
    
    cities = await services.get_cities(page=page, per_page=per_page)  

    logger.info(f"{request} {status_code} {detail}")
    return cities

@app.get("/api/download/city/", response_model=CityBase)
@logger.catch(exclude=HTTPException)
async def download_city(
    city_id: int,
    extension: float
): 
    request = f"GET /api/download/city?city_id={city_id}&extension={extension}/"
    status_code = 200
    detail = "OK"

    city = await services.download_city(city_id=city_id, extension=extension)
    if city is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise HTTPException(status_code=status_code, detail=detail)

    
    logger.info(f"{request} {status_code} {detail}")
    return city

@app.get("/api/delete/city/", response_model=CityBase)
@logger.catch(exclude=HTTPException)
async def delete_city(
    city_id: int
): 
    request = f"GET /api/delete/city?city_id={city_id}/"
    status_code = 200
    detail = "OK"

    city = await services.delete_city(city_id=city_id)
    if city is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise HTTPException(status_code=status_code, detail=detail)

    
    logger.info(f"{request} {status_code} {detail}")
    return city

@app.get("/api/regions/city/", response_model=List[RegionBase])
@logger.catch(exclude=HTTPException)
async def city_regions(
    city_id: int,
    depth: int
): 
    request = f"GET /api/regions/city?city_id={city_id}/"
    status_code = 200
    detail = "OK"

    regions = await services.get_regions(city_id=city_id, regions=regions_df, depth=depth)
    if regions is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise HTTPException(status_code=status_code, detail=detail)

    logger.info(f"{request} {status_code} {detail}")
    return regions
