export interface townBounds{
    maxlat: string,
    maxlon: string, 
    minlat: string,
    minlon: string
}

export enum districtLevels{
  city = 0,
  children = 1,
  subchildren = 2,
}

export interface _center{
  lat: number,
  lon: number
}

export type _coordinates = L.LatLngTuple[][] | L.LatLngTuple[]

export interface _district{
    type: string,
    properties: {
      osm_id: number,
      local_name: string,
    },
    geometry: {
      type: string,
      coordinates: _coordinates[],
    }
}
  
  export interface _distBounds{
    type: string,
    crs: {
      type: string,
      properties: {
        name: string
      }
    },
    features: _district[]
  }

export type _districts = {
  [key in districtLevels]: Region[]

}

export interface Region{
  id: number,
  depth: districtLevels,
  name: string,
  type: 'Polygon'
  regions: _coordinates
}


export interface Town{
  id : number,
  city_name: string,
  property: {
    population: number,
    population_density: number,
    center: {
      longitude: number,
      latitude: number
  },
    time_zone: string,
    time_created: string
  },
  downloaded: boolean,
    // id: string,
    // name: string,
    // map?: any,
    // file?: string,
    // districtFolder?: string,
    // image?: string,
    // bounds?: townBounds,
    // center: _center,
    districts: _districts
}