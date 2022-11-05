from database import engine, Base, SessionLocal
from models import City, CityProperty, Point
from schemas import CityBase, PropertyBase, PointBase, RegionBase
from typing import List, TYPE_CHECKING, Tuple
import pandas as pd
import osmnx as ox
import geopandas as gpd
import os.path


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

def add_tables():
    return Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:        
        db.close()

def point_to_scheme(point : Point) -> PointBase:
    if point is None:
        return None

    return PointBase(latitude=point.latitude, longitude=point.longitude)

def property_to_scheme(property : CityProperty, session : "Session") -> PropertyBase:
    if property is None:
        return None

    property_base = PropertyBase(population=property.population, population_density=property.population_density, time_zone=property.time_zone, time_created=str(property.time_created))
    point = session.query(Point).filter(Point.id==property.id_center).first()
    point_base = point_to_scheme(point=point)
    property_base.center = point_base
    
    return property_base

def city_to_scheme(city : City, session : "Session") -> CityBase:
    if city is None:
        return None

    city_base = CityBase(id=city.id, city_name=city.city_name, downloaded=city.downloaded)
    property = session.query(CityProperty).filter(CityProperty.id==city.id_property).first()
    property_base = property_to_scheme(property=property, session=session)
    city_base.property = property_base
    
    return city_base

def cities_to_scheme_list(cities : List[City], session : "Session") -> List[CityBase]:
    schemas = []
    for city in cities:
        schemas.append(city_to_scheme(city=city, session=session))
    return schemas

async def get_cities(page: int, per_page: int) -> List[CityBase]:
    with SessionLocal.begin() as session:
        cities = session.query(City).all()
        cities = cities[page * per_page : (page + 1) * per_page]
        return cities_to_scheme_list(cities, session)

async def get_city(city_id: int) -> CityBase:
    with SessionLocal.begin() as session:
        city = session.query(City).get(city_id)
        return city_to_scheme(city=city, session=session)

def add_info_to_db(city : pd.core.frame.DataFrame):
    with SessionLocal.begin() as session:
        city_name = city['Город']
        res = session.query(City).filter(City.city_name==city_name).first()
        if res is None:
            id = add_point_to_db(df=city)
            id = add_property_to_db(df=city, point_id=id)
            add_city_to_db(df=city, property_id=id)
            print(f'ADDED: {city_name}')
        else:
            print(f'ALREADY EXISTS: {city_name}')


def add_point_to_db(df : pd.core.frame.DataFrame):
    with SessionLocal.begin() as session:
        point = Point(latitude=df['Широта'], longitude=df['Долгота'])
        session.add(point)
        session.flush()
        return point.id

def add_property_to_db(df : pd.core.frame.DataFrame, point_id : int):
    with SessionLocal.begin() as session:
        # df['Федеральный округ']
        property = CityProperty(id_center=point_id, population=df['Население'], time_zone=df['Часовой пояс'])
        session.add(property)
        session.flush()
        return property.id

def add_city_to_db(df : pd.core.frame.DataFrame, property_id : int):
    with SessionLocal.begin() as session:
        city = City(city_name=df['Город'], id_property=property_id)
        session.add(city)
        session.flush()
        return city.id

def init_db():
    cities = pd.read_csv('./data/cities.csv')
    for row in range(0, cities.shape[0]):
        add_info_to_db(cities.loc[row, :])

def download_info(city : City, extension : float):
    filePath = f'./data/graphs/{city}.osm'
    if os.path.isfile(filePath):
        print(f'Exists: {filePath}')
        return True
    else:
        print(f'Loading: {filePath}')
        query = {'city': city.city_name}
        try:
            city_info = ox.geocode_to_gdf(query)

            north = city_info.iloc[0]['bbox_north']  
            south = city_info.iloc[0]['bbox_south']
            delta = (north-south) * extension / 200
            north += delta
            south -= delta

            east = city_info.iloc[0]['bbox_east'] 
            west = city_info.iloc[0]['bbox_west']
            delta = (east-west) * extension / 200
            east += delta
            west -= delta

            G = ox.graph_from_bbox(north=north, south=south, east=east, west=west, simplify=True, network_type='drive',)
            ox.save_graph_xml(G, filepath=filePath)
            return True

        except ValueError:
            print('Invalid city name')
            return False

def delete_info(city : City):
    filePath = f'./data/graphs/{city}.osm'
    if os.path.isfile(filePath):
        os.remove(filePath)
        print(f'Deleted: {filePath}')
        return True
    else:
        print(f"File doesn't exist: {filePath}")
        return False
        

async def download_city(city_id : int, extension : float) -> CityBase:
    with SessionLocal.begin() as session:
        city = session.query(City).get(city_id)
        if city is None:
            return None
            
        city.downloaded = download_info(city=city, extension=extension)
        session.flush()
        return city_to_scheme(city=city, session=session)

async def delete_city(city_id : int) -> CityBase:
    with SessionLocal.begin() as session:
        city = session.query(City).get(city_id)
        if city is None:
            return None
            
        delete_info(city=city)
        city.downloaded = False
        session.flush()
        return city_to_scheme(city=city, session=session)

def to_json_array(polygon_str : str):
    polygon_str = polygon_str.replace('MULTILINESTRING ', '').replace('LINESTRING ', '')
    polygon_str = polygon_str.replace(', ', '],[').replace(' ', ',')
    polygon_str = polygon_str.replace('(', '[').replace(')', ']')
    polygon_str = "[" + polygon_str + ']'
    return polygon_str

def region_to_scheme(regions : gpd.geodataframe.GeoDataFrame, ids_list : List[int], depth : int) -> Tuple[RegionBase, List[int]]:
    polygons = regions[regions['osm_id'].isin(ids_list)]
    ids_list = regions[regions['parents'].str.contains('|'.join(str(x) for x in ids_list), na=False)]['osm_id'].to_list()
    region = RegionBase(admin_level=depth, regions=to_json_array(str(polygons.iloc[0]['geometry'].boundary)))
    return region, ids_list

def regions_to_scheme(city : City) -> List[RegionBase]:
    regions = gpd.read_file('./data/regions.json', driver='GeoJSON')
    regions_list = []

    ids_list = regions[regions['local_name']==city.city_name]['osm_id'].to_list()
    depth = 0
    while len(ids_list) != 0:
        region, ids_list = region_to_scheme(regions=regions, ids_list=ids_list, depth=depth)
        regions_list.append(region)
        depth += 1
        
    return regions_list

async def get_regions(city_id : int) -> List[RegionBase]:
    with SessionLocal.begin() as session:
        city = session.query(City).get(city_id)
        if city is None:
            return None

        return regions_to_scheme(city=city)
