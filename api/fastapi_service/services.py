from database import engine, Base, SessionLocal, database
from models import City, CityProperty, Point
from shapely.geometry.point import Point as ShapelyPoint
from database import *
from schemas import CityBase, PropertyBase, PointBase, RegionBase, GraphBase
from shapely.geometry.multilinestring import MultiLineString
from shapely.geometry.linestring import LineString
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union
from geopandas.geodataframe import GeoDataFrame
from pandas.core.frame import DataFrame
from osm_handler import parse_osm
from typing import List, TYPE_CHECKING
from sqlalchemy import update, text

import pandas as pd
import osmnx as ox
import os.path
import ast
import io
import pandas as pd
import networkx as nx
import time

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

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

def list_to_csv_str(data, columns : List['str']):
    buffer = io.StringIO()
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(buffer, index=False)
    return buffer.getvalue(), df

def reversed_graph_to_csv_str(edges_df : DataFrame):
    # redges_df, rnodes_df, rmatrix_df = get_reversed_graph(edges_df, 
    #                                                       source='source', 
    #                                                       target='target', 
    #                                                       merging_column='id_way', 
    #                                                       empty_cell_sign='', 
    #                                                       edge_attr=['id_way'])

    redges = io.StringIO()
    rnodes = io.StringIO()
    # rmatrix = io.StringIO()

    # redges_df.to_csv(redges, index=False)
    # rnodes_df.to_csv(rnodes, index=False)
    # rmatrix_df.to_csv(rmatrix, index=False)

    pd.read_csv('./data/reversed_edges.csv').to_csv(redges, index=False)
    pd.read_csv('./data/reversed_nodes.csv').to_csv(rnodes, index=False)
    
    return redges.getvalue(), rnodes.getvalue(), None

def graph_to_scheme(points, edges, pprop, wprop) -> GraphBase:
    edges_str, edges_df = list_to_csv_str(edges, ['id', 'id_way', 'source', 'target', 'name'])
    points_str, _ = list_to_csv_str(points, ['id', 'longitude', 'latitude'])
    pprop_str, _ = list_to_csv_str(pprop, ['id', 'property', 'value'])
    wprop_str, _ = list_to_csv_str(wprop, ['id', 'property', 'value'])

    r_edges_str, r_nodes_str, r_matrix_str = reversed_graph_to_csv_str(edges_df)

    return GraphBase(edges_csv=edges_str, points_csv=points_str, 
                     ways_properties_csv=wprop_str, points_properties_csv=pprop_str,
                     reversed_edges_csv=r_edges_str, reversed_nodes_csv=r_nodes_str)
                    #  reversed_matrix_csv=r_matrix_str)

async def property_to_scheme(property : CityProperty) -> PropertyBase:
    if property is None:
        return None

    return PropertyBase(population=property.population, population_density=property.population_density, 
                        time_zone=property.time_zone, time_created=str(property.time_created),
                        c_latitude = property.c_latitude, c_longitude = property.c_longitude)

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
            oneway = False
            if "oneway" in way_dict.keys() and way_dict['oneway'] == "yes": # доделать oneway
                oneway = True
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
        return None, None, None, None
    return await graph_from_poly(city_id=city_id, polygon=polygon)
    
def point_obj_to_list(db_record) -> List:
    return [db_record.id, db_record.longitude, db_record.latitude]

def edge_obj_to_list(db_record) -> List:
    return [db_record.id, db_record.id_way, db_record.id_src, db_record.id_dist, db_record.value]

def record_obj_to_wprop(record):
    return [record.id_way ,record.property ,record.value]

def record_obj_to_pprop(record):
    return [record.id_point ,record.property ,record.value]

async def graph_from_poly(city_id, polygon):
    bbox = polygon.bounds   # min_lon, min_lat, max_lon, max_lat

    q = CityAsync.select().where(CityAsync.c.id == city_id)
    city = await database.fetch_one(q)
    if city is None or not city.downloaded:
        return None, None, None, None
    query = text(
        f"""SELECT "Points".id, "Points".longitude, "Points".latitude FROM 
        (SELECT id_src FROM "Edges" JOIN 
        (SELECT "Ways".id as way_id FROM "Ways" WHERE "Ways".id_city = {city_id})AS w ON "Edges".id_way = w.way_id) AS p JOIN "Points" ON p.id_src = "Points".id
        WHERE "Points".longitude < {bbox[2]} and "Points".longitude > {bbox[0]} and "Points".latitude > {bbox[1]} and "Points".latitude < {bbox[3]};
        """)
    res = await database.fetch_all(query)
    points = list(map(point_obj_to_list, res)) # [...[id, longitude, latitude]...]
    q = PropertyAsync.select().where(PropertyAsync.c.property == 'name')
    prop = await database.fetch_one(q)
    prop_id = prop.id
    query = text(
        f"""SELECT id, id_way, id_src, id_dist, value FROM 
        (SELECT id, "Edges".id_way, id_src, id_dist, value FROM "Edges" JOIN 
        (SELECT id_way, value FROM "WayProperties" WHERE id_property = {prop_id}) AS q ON "Edges".id_way = q.id_way) AS a JOIN 
        (SELECT "Points".id as point_id FROM 
        (SELECT id_src FROM "Edges" JOIN 
        (SELECT "Ways".id as way_id FROM "Ways" WHERE "Ways".id_city = {city_id}) AS w ON "Edges".id_way = w.way_id) AS p JOIN "Points" ON
        p.id_src = "Points".id WHERE "Points".longitude < {bbox[2]} and "Points".longitude > {bbox[0]} and "Points".latitude > {bbox[1]} and "Points".latitude < {bbox[3]}) AS b ON a.id_src = b.point_id; 
        """)
    res = await database.fetch_all(query)
    edges = list(map(edge_obj_to_list, res)) # [...[id, id_way, from, to, name]...]

    points, edges, ways_prop_ids, points_prop_ids  = filter_by_polygon(polygon=polygon, edges=edges, points=points)
    conn = engine.connect()

    ids_ways = build_or_query('id_way', ways_prop_ids)
    query = text(
        f"""SELECT id_way, property, value FROM 
        (SELECT id_way, id_property, value FROM "WayProperties" WHERE {ids_ways}) AS p 
        JOIN "Properties" ON p.id_property = "Properties".id;
        """)

    res = conn.execute(query).fetchall()
    ways_prop = list(map(record_obj_to_wprop, res))

    ids_points = build_or_query('id_point', points_prop_ids)
    query = text(
        f"""SELECT id_point, property, value FROM 
        (SELECT id_point, id_property, value FROM "PointProperties" WHERE {ids_points}) AS p 
        JOIN "Properties" ON p.id_property = "Properties".id;
        """)

    res = conn.execute(query).fetchall()
    points_prop = list(map(record_obj_to_pprop, res))

    return points, edges, points_prop, ways_prop    

def build_or_query(query_field : str, data_set : set()):
    buffer = ''
    for element in data_set:
        buffer += f'{query_field} = {element} OR '

    return buffer[0:len(buffer)-4]

def filter_by_polygon(polygon, edges, points):
    points_ids = set()
    ways_prop_ids = set()
    points_filtred = []
    edges_filtred = []

    for point in points:
        lon = point[1]
        lat = point[2]
        if polygon.contains(ShapelyPoint(lon, lat)):
            points_ids.add(point[0])
            points_filtred.append(point)

    for edge in edges:
        id_from = edge[2]
        id_to = edge[3]
        if (id_from in points_ids) and (id_to in points_ids):
            edges_filtred.append(edge)
            ways_prop_ids.add(edge[1])

    return points_filtred, edges_filtred, ways_prop_ids, points_ids


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

nodata = '-'
merging_col = 'id_way'


def union_and_delete(graph):
    edge_to_remove = list()

    for source, target, attributes in graph.edges(data=True):
        attributes['node_id'] = {source, target}
        attributes['cross_ways'] = set()
        try:
            for id1, id2, attr in graph.edges(data=True):
                if source == id1 and target == id2:
                    continue
                if (attributes[merging_col] == attr[merging_col] and attributes[merging_col] != nodata) \
                        and len(attributes['node_id'].intersection(attr['node_id'])):
                    attributes['node_id'] = attributes['node_id'].union(attr['node_id'])
                    attr['node_id'].clear()
                    edge_to_remove.append((id1, id2))
                elif (attributes[merging_col] != attr[merging_col] or attributes[merging_col] == nodata) \
                        and len(attributes['node_id'].intersection({id1, id2})):
                    if attr[merging_col] != nodata:
                        attributes['cross_ways'].add(attr[merging_col])
                    else:
                        attributes['cross_ways'].add(str(id1) + str(nodata) + str(id2))
        except:
            continue

    graph.remove_edges_from(edge_to_remove)


def reverse_graph(graph):
    new_graph = nx.Graph()

    new_graph.add_nodes_from([(attr[merging_col], attr) if attr[merging_col] != nodata
                              else (str(source) + str(nodata) + str(target), attr)
                              for source, target, attr in graph.edges(data=True)])

    for node_id, attributes in new_graph.nodes(data=True):
        for id in new_graph.nodes():
            if id in attributes['cross_ways']:
                new_graph.add_edge(node_id, id)

    return new_graph


def convert_to_df(graph, source='source', target='target'):
    edges_df = nx.to_pandas_edgelist(graph, source='source_way', target='target_way')
    nodes_df = pd.DataFrame.from_dict(graph.nodes, orient='index')

    return edges_df, nodes_df


def get_reversed_graph(graph, source='source', target='target', merging_column='way_id', empty_cell_sign='-',
                       edge_attr=['way_id']):
    global nodata
    global merging_col
    nodata = empty_cell_sign
    merging_col = merging_column

    nx_graph = nx.from_pandas_edgelist(graph, source=source, target=target, edge_attr=edge_attr)
    adjacency_df = nx.to_pandas_adjacency(nx_graph, weight=merging_column, dtype=int)
    union_and_delete(nx_graph)

    new_graph = reverse_graph(nx_graph)
    edges_ds, nodes_df = convert_to_df(new_graph, source='source_way', target='target_way')
    return edges_ds, nodes_df, adjacency_df

