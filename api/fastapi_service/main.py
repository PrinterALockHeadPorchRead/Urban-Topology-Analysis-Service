from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from uvicorn import run
from os import getenv
from schemas import CityBase, RegionBase
from database import database, engine, metadata

import pandas as pd
import geopandas as gpd
import services
import logs 

regions_df = gpd.read_file('./data/regions.json', driver='GeoJSON')
cities_info = pd.read_csv('./data/cities.csv')
app = FastAPI()
logger = logs.init()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()
    services.init_db(cities_info=cities_info)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

if __name__ == "__main__":
    metadata.create_all(engine)
    run("main:app", host="0.0.0.0", port=getenv("PORT", 8002), reload=True)

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
    page: int = Query(ge=0), 
    per_page : int = Query(gt=0)
): 
    request = f"GET /api/cities?page={page}&per_page={per_page}/"
    status_code = 200
    detail = "OK"

    cities = await services.get_cities(page=page, per_page=per_page)  

    logger.info(f"{request} {status_code} {detail}")
    return cities


@app.get("/api/regions/city/", response_model=List[RegionBase])
@logger.catch(exclude=HTTPException)
async def city_regions(
    city_id: int
): 
    request = f"GET /api/regions/city?city_id={city_id}/"
    status_code = 200
    detail = "OK"

    regions = services.get_regions(city_id=city_id, regions=regions_df, cities=cities_info)
    if regions is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise HTTPException(status_code=status_code, detail=detail)

    logger.info(f"{request} {status_code} {detail}")
    return regions


@app.post('/api/city/graph/region/')
@logger.catch(exclude=HTTPException)
async def city_graph(
    city_id: int,
    regions_ids: List[int],
):
    request = f"GET /api/cities/graph/?city_id={city_id}&regions={regions_ids}"
    status_code = 200
    detail = "OK"

    points, edges, pprop, wprop  = await services.graph_from_ids(city_id=city_id, regions_ids=regions_ids, regions=regions_df)
    if points is None or edges is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise HTTPException(status_code=status_code, detail=detail)

    edges_df = pd.DataFrame(edges, columns=['id', 'id_way', 'from', 'to', 'name']).to_csv(sep=',', index=False)
    points_df = pd.DataFrame(points, columns=['id', 'longitude', 'latitude']).to_csv(sep=',', index=False)
    pprop_df = pd.DataFrame(pprop, columns=['id', 'property', 'value']).to_csv(sep=',', index=False)
    wprop_df = pd.DataFrame(wprop, columns=['id', 'property', 'value']).to_csv(sep=',', index=False)

    return StreamingResponse( #2 файла не отсылаются, исправить
        iter([pprop_df]),
        media_type='text/csv',
        headers={"Content-Disposition":
                f"attachment;filename=<{city_id}_{regions_ids}>.csv"})


@app.post('/api/city/graph/bbox/{city_id}/')
@logger.catch(exclude=HTTPException)
async def city_graph_poly(
    city_id: int,
    polygons_as_list:  List[List[List[float]]]
):
    request = f"POST /api/city/graph/bbox/{city_id}/"
    status_code = 200
    detail = "OK"

    polygon = services.list_to_polygon(polygons=polygons_as_list)
    points, edges, pprop, wprop = await services.graph_from_poly(city_id=city_id, polygon=polygon)
    
    if points is None:
        status_code = 404
        detail = "NOT FOUND"
        logger.error(f"{request} {status_code} {detail}")
        raise HTTPException(status_code=status_code, detail=detail)

    edges_df = pd.DataFrame(edges, columns=['id', 'id_way', 'from', 'to', 'name']).to_csv(sep=',', index=False)
    points_df = pd.DataFrame(points, columns=['id', 'longitude', 'latitude']).to_csv(sep=',', index=False)
    pprop_df = pd.DataFrame(pprop, columns=['id', 'property', 'value']).to_csv(sep=',', index=False)
    wprop_df = pd.DataFrame(wprop, columns=['id', 'property', 'value']).to_csv(sep=',', index=False)

    return StreamingResponse( #2 файла не отсылаются, исправить
    iter([edges_df]),
    media_type='text/csv',
    headers={"Content-Disposition":
             f"attachment;filename=<{city_id}>.csv"})



# Useless:

# @app.delete("/api/delete/city/", response_model=CityBase)
# @logger.catch(exclude=HTTPException)
# async def delete_city(
#     city_id: int
# ): 
#     request = f"GET /api/delete/city?city_id={city_id}/"
#     status_code = 200
#     detail = "OK"

#     city = await services.delete_city(city_id=city_id)
#     if city is None:
#         status_code = 404
#         detail = "NOT FOUND"
#         logger.error(f"{request} {status_code} {detail}")
#         raise HTTPException(status_code=status_code, detail=detail)

#     logger.info(f"{request} {status_code} {detail}")
#     return city

# @app.get("/api/download/city/", response_model=CityBase)
# @logger.catch(exclude=HTTPException)
# async def download_city(
#     city_id: int,
#     extension: float
# ): 
#     request = f"GET /api/download/city?city_id={city_id}&extension={extension}/"
#     status_code = 200
#     detail = "OK"

#     city = await services.download_city(city_id=city_id, extension=extension)
#     if city is None:
#         status_code = 404
#         detail = "NOT FOUND"
#         logger.error(f"{request} {status_code} {detail}")
#         raise HTTPException(status_code=status_code, detail=detail)

#     logger.info(f"{request} {status_code} {detail}")
#     return city
