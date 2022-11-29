from database import engine, Base, SessionLocal, database
from models import City, CityProperty, Point
from database import *
from schemas import CityBase, PropertyBase, PointBase, RegionBase
from shapely.geometry.multilinestring import MultiLineString
from shapely.geometry.linestring import LineString
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union
from geopandas.geodataframe import GeoDataFrame
from pandas.core.frame import DataFrame
from osm_handler import parse_osm
from typing import List, TYPE_CHECKING
from sqlalchemy import update, text
import osmnx as ox
import os.path
import ast

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

async def property_to_scheme(property : CityProperty) -> PropertyBase:
    if property is None:
        return None

    property_base = PropertyBase(population=property.population, population_density=property.population_density, time_zone=property.time_zone, time_created=str(property.time_created))
    query = PointAsync.select().where(PointAsync.c.id == property.id_center)
    point = await database.fetch_one(query)
    point_base = point_to_scheme(point=point)
    property_base.center = point_base
    
    return property_base

async def city_to_scheme(city : City) -> CityBase:
    if city is None:
        return None

    city_base = CityBase(id=city.id, city_name=city.city_name, downloaded=city.downloaded)
    query = CityPropertyAsync.select().where(CityPropertyAsync.c.id == city.id_property)
    property = await database.fetch_one(query)
    property_base = await property_to_scheme(property=property)
    city_base.property = property_base
    
    return city_base

async def cities_to_scheme_list(cities : List[City]) -> List[CityBase]:
    schemas = []
    for city in cities:
        schemas.append(await city_to_scheme(city=city))
    return schemas

async def get_cities(page: int, per_page: int) -> List[CityBase]:
    query = CityAsync.select()
    cities = await database.fetch_all(query)
    cities = cities[page * per_page : (page + 1) * per_page]
    return await cities_to_scheme_list(cities)

async def get_city(city_id: int) -> CityBase:
    query = CityAsync.select().where(CityAsync.c.id == city_id)
    city = await database.fetch_one(query)
    return await city_to_scheme(city=city)

def add_info_to_db(city_df : DataFrame):
    city_name = city_df['Город']
    query = CityAsync.select().where(CityAsync.c.city_name == city_name)
    conn = engine.connect()
    city_db = conn.execute(query).first()
    downloaded = False
    if city_db is None:
        property_id = add_property_to_db(df=city_df)
        city_id = add_city_to_db(df=city_df, property_id=property_id)
    else:
        downloaded = city_db.downloaded
        city_id = city_db.id
    conn.close()
    file_path = f'./data/cities_osm/{city_name}.osm'
    if (not downloaded) and (os.path.exists(file_path)):
        print("ANDO NOW IM HERE")
        add_graph_to_db(city_id=city_id, file_path=file_path)


def add_graph_to_db(city_id : int, file_path : str):
        ways, nodes = parse_osm(file_path)

        conn = engine.connect()
        for key in nodes.keys():
            point_dict = nodes[key]
            lat = point_dict.pop('lat')
            lon = point_dict.pop('lon')
            try:
                query = PointAsync.insert().values(id=f"{key}", latitude=f'{lat}', longitude=f'{lon}')
                res = conn.execute(query)
            except:
                pass
            for key2 in point_dict.keys():
                try:
                    query = PropertyAsync.select().where(PropertyAsync.c.property == f"{key2}")
                    prop = conn.execute(query).first()
                except:
                    pass
                if prop != None:
                    prop_id = prop.id
                else:
                    try:
                        query = PropertyAsync.insert().values(property=f"{key2}")
                        prop_id = conn.execute(query).inserted_primary_key[0]
                        prop_id = int(prop_id)
                    except:
                        pass
                try:
                    query = PointPropertyAsync.insert().values(id_point=f"{key}",id_property=f"{prop_id}", value = f"{point_dict[key2]}")
                    res = conn.execute(query)
                except:
                    pass

        for key in ways.keys():
            try:
                query = WayAsync.insert().values(id = f"{key}", id_city = f"{city_id}")
                conn.execute(query)
            except:
                pass
            graph = ways[key].pop('graph')
            way_dict = ways[key]
            oneway=False
            if "oneway" in way_dict.keys() and way_dict['oneway'] == "yes": # доделать oneway
                oneway=True
            for edge in graph:
                try:
                    query = EdgesAsync.insert().values(id_way = f'{key}', id_src=f'{edge[0]}', id_dist=f'{edge[1]}')
                    res = conn.execute(query)
                except:
                    pass
                if not oneway:
                    try:
                        query = EdgesAsync.insert().values(id_way = f'{key}', id_src=f'{edge[1]}', id_dist=f'{edge[0]}')
                        res = conn.execute(query)
                    except:
                        pass
                
            for key2 in way_dict.keys():
                try:
                    query = PropertyAsync.select().where(PropertyAsync.c.property == f"{key2}")
                    prop = conn.execute(query).first()
                except:
                    pass
                if prop != None:
                    prop_id = prop.id
                else:
                    try:
                        query = PropertyAsync.insert().values(property=f"{key2}")
                        prop_id = conn.execute(query).inserted_primary_key[0]
                        prop_id = int(prop_id)
                    except:
                        pass
                try:
                    query = WayPropertyAsync.insert().values(id_way=f'{key}',id_property=f'{prop_id}', value = f'{way_dict[key2]}')
                    conn.execute(query)
                except:
                    pass
        query = update(CityAsync).where(CityAsync.c.id == f"{city_id}").values(downloaded = True)
        conn.execute(query)
        conn.close()

def add_point_to_db(df : DataFrame) -> int:
    with SessionLocal.begin() as session:
        point = Point(latitude=df['Широта'], longitude=df['Долгота'])
        session.add(point)
        session.flush()
        return point.id

def add_property_to_db(df : DataFrame) -> int:
    with SessionLocal.begin() as session:
        property = CityProperty(c_latitude=df['Широта'], c_longitude=df['Долгота'], population=df['Население'], time_zone=df['Часовой пояс'])
        session.add(property)
        session.flush()
        return property.id

def add_city_to_db(df : DataFrame, property_id : int) -> int:
    with SessionLocal.begin() as session:
        city = City(city_name=df['Город'], id_property=property_id)
        session.add(city)
        session.flush()
        return city.id

def init_db(cities_info : DataFrame):
    for row in range(0, cities_info.shape[0]):
        add_info_to_db(cities_info.loc[row, :])


async def download_info(city : City, extension : float) -> bool:
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

def delete_info(city : City) -> bool:
    filePath = f'./data/graphs/{city}.osm'
    if os.path.isfile(filePath):
        os.remove(filePath)
        print(f'Deleted: {filePath}')
        return True
    else:
        print(f"File doesn't exist: {filePath}")
        return False
        

async def download_city(city_id : int, extension : float) -> CityBase:
    query = CityAsync.select().where(CityAsync.c.id == city_id)
    city = await database.fetch_one(query)
    if city is None:
        return None
        
    city.downloaded = await download_info(city=city, extension=extension)

    return city_to_scheme(city=city)

async def delete_city(city_id : int) -> CityBase:
    query = CityAsync.select().where(CityAsync.c.id == city_id)
    city = await database.fetch_one(query)
    if city is None:
        return None
        
    delete_info(city=city)
    city.downloaded = False
    return await city_to_scheme(city=city)

def to_list(polygon : LineString):
    list = []
    for x, y in polygon.coords:
        list.append([x, y])
    return list

def to_json_array(polygon):
    coordinates_list = []
    if type(polygon) == LineString:
       coordinates_list.append(to_list(polygon))
    elif type(polygon) == MultiLineString:
        for line in polygon.geoms:
            coordinates_list.append(to_list(line))
    else:
        raise ValueError("polygon must be type of LineString or MultiLineString")

    return coordinates_list

def region_to_schemas(regions : GeoDataFrame, ids_list : List[int], admin_level : int) -> List[RegionBase]:
    regions_list = [] 
    polygons = regions[regions['osm_id'].isin(ids_list)]
    for _, row in polygons.iterrows():
        id = row['osm_id']
        name = row['local_name']
        regions_array = to_json_array(row['geometry'].boundary)
        base = RegionBase(id=id, name=name, admin_level=admin_level, regions=regions_array)
        regions_list.append(base)

    return regions_list

def children(ids_list : List[int], admin_level : int, regions : GeoDataFrame):
    area = regions[regions['parents'].str.contains('|'.join(str(x) for x in ids_list), na=False)]
    area = area[area['admin_level']==admin_level]
    lst = area['osm_id'].to_list()
    if len(lst) == 0:
        return ids_list, False
    return lst, True

def get_admin_levels(city : City, regions : GeoDataFrame, cities : DataFrame) -> List[RegionBase]:
    regions_list = []

    levels_str = cities[cities['Город'] == city.city_name]['admin_levels'].values[0]
    levels = ast.literal_eval(levels_str)

    info = regions[regions['local_name']==city.city_name].sort_values(by='admin_level')
    ids_list = [info['osm_id'].to_list()[0]]

    schemas = region_to_schemas(regions=regions, ids_list=ids_list, admin_level=levels[0])
    regions_list.extend(schemas)
    for level in levels:
        ids_list, data_valid = children(ids_list=ids_list, admin_level=level, regions=regions)
        if data_valid:
            schemas = region_to_schemas(regions=regions, ids_list=ids_list, admin_level=level)
            regions_list.extend(schemas)

    return regions_list



def get_regions(city_id : int, regions : GeoDataFrame, cities : DataFrame) -> List[RegionBase]:
    with SessionLocal.begin() as session:
        city = session.query(City).get(city_id)
        if city is None:
            return None
        return get_admin_levels(city=city, regions=regions, cities=cities)

async def graph_from_poly(city_id, polygon):
    print(polygon.bounds) #min_lon, min_lat, max_lon, max_lat
    return None

def list_to_polygon(polygons : List[List[List[float]]]):
    return unary_union([Polygon(polygon) for polygon in polygons])

def polygons_from_region(regions_ids : List[int], regions : GeoDataFrame):
    if len(regions_ids) == 0:
        return None
    polygons = regions[regions['osm_id'].isin(regions_ids)]
    return unary_union([geom for geom in polygons['geometry'].values])

async def graph_from_ids(city_id : int, regions_ids : List[int], regions : GeoDataFrame):
    polygon = polygons_from_region(regions_ids=regions_ids, regions=regions)
    if polygon == None:
        return None
    return graph_from_poly(city_id=city_id, polygon=polygon)
    
def point_obj_to_list(db_record) -> List:
    return [db_record.id, db_record.longitude, db_record.latitude]

def edge_obj_to_list(db_record) -> List:
    return [db_record.id, db_record.id_src, db_record.id_dist, db_record.value]

async def graph_from_id(city_id, region_id): #реализован механизм доставания точек и ребер города по id
    q = CityAsync.select().where(CityAsync.c.id == city_id)
    city = await database.fetch_one(q)
    if city is None or not city.downloaded: # add region check
        return None
    query = text(
        f"""
        SELECT "Points".id, "Points".longitude, "Points".latitude
        FROM (SELECT id_src FROM "Edges" JOIN 
        (SELECT "Ways".id as way_id FROM "Ways" WHERE "Ways".id_city = {city_id})AS w ON "Edges".id_way = w.way_id) AS p
        JOIN "Points" ON p.id_src = "Points".id;
        """)
    res = await database.fetch_all(query)

    points = list(map(point_obj_to_list,res)) # [...[id, longitude, latitude]...]
    q = PropertyAsync.select().where(PropertyAsync.c.property == 'name')
    prop = await database.fetch_one(q)
    prop_id = prop.id
    query = text(
        f""" SELECT id, id_src, id_dist, value FROM 
        (SELECT id, id_src, id_dist, id_way FROM "Edges" JOIN 
        (SELECT "Ways".id as way_id FROM "Ways" WHERE "Ways".id_city = {city_id}) AS w ON "Edges".id_way = w.way_id) e JOIN 
        (SELECT id_way, value FROM "WayProperties" WHERE id_property = {prop_id}) p ON e.id_way = p.id_way;
        """)
    res = await database.fetch_all(query)
    edges = list(map(point_obj_to_list,res)) # [...[id, from, to, name]...]

    return points, edges

def bbox_from_poly():
    pass

async def graph_from_poly(city_id,polygon):
    bbox = bbox_from_poly(polygon)
    q = CityAsync.select().where(CityAsync.c.id == city_id)
    city = await database.fetch_one(q)
    if city is None or not city.downloaded:
        return None
    query = text(
        f"""SELECT "Points".id, "Points".longitude, "Points".latitude FROM 
        (SELECT id_src FROM "Edges" JOIN 
        (SELECT "Ways".id as way_id FROM "Ways" WHERE "Ways".id_city = {city_id})AS w ON "Edges".id_way = w.way_id) AS p JOIN "Points" ON p.id_src = "Points".id
        WHERE "Points".longitude < {bbox['?']} and "Points".longitude > {bbox['?']} and "Points".latitude > {bbox['?']} and "Points".latitude < {bbox['?']};
        """)
    res = await database.fetch_all(query)
    points = list(map(point_obj_to_list,res)) # [...[id, longitude, latitude]...]
    q = PropertyAsync.select().where(PropertyAsync.c.property == 'name')
    prop = await database.fetch_one(q)
    prop_id = prop.id
    query = text(
        f"""SELECT id, id_src, id_dist, value FROM 
        (SELECT id, id_src, id_dist, value FROM "Edges" JOIN 
        (SELECT id_way, value FROM "WayProperties" WHERE id_property = {prop_id}) AS q ON "Edges".id_way = q.id_way) AS a JOIN 
        (SELECT "Points".id as point_id FROM 
        (SELECT id_src FROM "Edges" JOIN 
        (SELECT "Ways".id as way_id FROM "Ways" WHERE "Ways".id_city = {city_id}) AS w ON "Edges".id_way = w.way_id) AS p JOIN "Points" ON
        p.id_src = "Points".id WHERE "Points".longitude < {bbox['?']} and "Points".longitude > {bbox['?']} and "Points".latitude > {bbox['?']} and "Points".latitude < {bbox['?']}) AS b ON a.id_src = b.point_id; 
        """)
    res = await database.fetch_all(query)
    edges = list(map(point_obj_to_list,res)) # [...[id, from, to, name]...]

    return points, edges




query_for_citypoints_v1 = """
SELECT "Points".id, "Points".longitude, "Points".latitude FROM (SELECT id_src FROM "Edges" JOIN (SELECT "Ways".id as way_id FROM "Ways" WHERE "Ways".id_city = 110)AS w ON "Edges".id_way = w.way_id) AS p JOIN "Points" ON p.id_src = "Points".id;
"""

query_for_cityp_bbox_v1 = """
SELECT "Points".id, "Points".longitude, "Points".latitude FROM (SELECT id_src FROM "Edges" JOIN (SELECT "Ways".id as way_id FROM "Ways" WHERE "Ways".id_city = 110)AS w ON "Edges".id_way = w.way_id) AS p JOIN "Points" ON p.id_src = "Points".id WHERE "Points".longitude < 91.4 and "Points".longitude > 91.395 and "Points".latitude > 53.75 and "Points".latitude < 53.77;
"""

query_for_edges_wnames_v1="""
SELECT id, id_src, id_dist, value FROM (SELECT id, id_src, id_dist, id_way FROM "Edges" JOIN (SELECT
"Ways".id as way_id FROM "Ways" WHERE "Ways".id_city = 110) AS w ON "Edges".id_way = w.way_id) e JOIN (SELECT id_way, value FROM "WayProperties" WHERE id_property = 3) p ON e.id_way = p.id_way;
"""

q = """
SELECT "Points".id, "Points".latitude FROM (SELECT id_src FROM "Edges" JOIN (SELECT "Ways".id as way_id FROM "Ways" WHERE "Ways".id_city = 110) AS w ON "Edges".id_way = w.way_id) AS p JOIN "Points" ON p.id_src = "Points".id WHERE "Points".longitude > 91.4;
"""
