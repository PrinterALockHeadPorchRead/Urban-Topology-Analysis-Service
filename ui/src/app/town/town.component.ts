import {ChangeDetectorRef, Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Region, Town, _distBounds } from '../interfaces/town';
import { FileService } from '../services/file.service';
import { TownService } from '../services/town.service';
import { GraphDataSrvice, GraphData, INode, Edge } from '../services/graph-data.service';

import * as L from 'leaflet'; //* - все

enum sections{
  map = 'map',
  graph = 'graph',
  roads = 'roads'
}


@Component({
  selector: 'app-town',
  templateUrl: './town.component.html',
  styleUrls: ['./town.component.css', './loader.css']
})
export class TownComponent implements OnInit{

  id?: number;
  town?: Town;
  RgraphData?: GraphData;
  LgraphData?: GraphData;
  graphName = '';
  // roadBounds?: L.LatLngBounds;
  loading: boolean = false;

  private _section: sections = sections.map;
  set section(val: sections | string){
    this._section = val as sections;
    const achor = document.getElementsByName(val)[0];
    achor?.scrollIntoView({behavior: 'smooth'});
  } get section(){return this._section}; // section=val вызывает set section(val), val=section вызывает get section

  constructor(
    private townService: TownService,
    private route: ActivatedRoute,
    private router: Router,
    private fileService: FileService,
    private cdRef: ChangeDetectorRef,
    private graphDataService: GraphDataSrvice
  ) { 
    this.section = sections.map;
    this.route.paramMap.subscribe(params=>{
      let id = params.get('id');
      if(id){
        this.id= Number(id);
        this.townService.getTown( id ).subscribe(
          town=>{
            this.town = town;
            this.getDistricts(town);
          },
          error=>{this.router.navigate(['/towns'])}
        )
      } else {
        this.router.navigate(['/towns']);
      }
    })
  }

  ngOnInit(): void {}

  getCenter(): L.LatLngTuple{
    if(!this.town) return [59.9414, 30.3267];
    return [ this.town.property.c_latitude, this.town.property.c_longitude ];
  }

  getDistricts(town: Town): void{
    this.townService.getTownRegions(town.id).subscribe(res => {
      const levels: any = {};
      res.forEach(value => {
        if( !levels[value.admin_level] ) levels[value.admin_level] = [];

        levels[value.admin_level].push(value);
      })
      town.districts = Object.keys(levels).map(key => levels[key]);
    })
  }

  handlePolygon(ev: {name: string, regionId?: number, polygon?: any}){
    if(!this.id) return;
    this.graphName = ev.name;

    if(ev.regionId){
      this.loading = true;
      this.cdRef.detectChanges();
      this.townService.getGraphFromId(this.id, ev.regionId).subscribe(res => {
        // console.log(res)
        this.getRgraph(res.points_csv, res.edges_csv);
        this.getLgraph(res.reversed_nodes_csv, res.reversed_edges_csv);
        this.loading = false;
        this.section = sections.graph;
        this.cdRef.detectChanges();
      })
      return;
    }
    if(ev.polygon){
      this.getGraphData(ev.polygon.getLatLngs()[0]);
      return;
    }
    // this.roadBounds = (ev.polygon as L.Polygon)?.getBounds();
  }
  
  getGraphData(nodes: L.LatLng[]){
    if(!this.id) return;
    const body: [number, number][] = nodes.map(node => [node.lng, node.lat]);
    this.townService.getGraphFromBbox(this.id, body).subscribe(console.log);
  }

  getRgraph(nodes_str: string, edges_str: string){
    const nodes: { [key: string]: INode } = {};
    const edges: { [key: string]: Edge } = {};

    const node_lines = nodes_str.split('\n')
    node_lines.slice(1).forEach((line, index) => {
      const [id, longitude, latitude] = line.split(',');
      if(id){
        nodes[Number(id)] = {
          lat: Number(latitude),
          lon: Number(longitude),
          way_id: 0
        }
      }
    })

    const edge_lines = edges_str.split('\n')
    edge_lines.slice(1).forEach((line, index) => {
      const [id,id_way,source,target,name] = line.split(',');
      if(id){
        edges[Number(id)] = {
          from: source,
          to: target,
          id: id,
          way_id: id_way,
          name: name
        }
      }
    })

    this.RgraphData = {
      nodes: nodes,
      edges: edges
    }
    // console.log(this.RgraphData)
  }
  
  getLgraph(nodes_str: string, edges_str: string){
    const nodes: { [key: string]: INode } = {};
    const edges: { [key: string]: Edge } = {};

    const names = this.RgraphData ? Object.values(this.RgraphData.edges).map(edge => ({id: edge.way_id, name: edge.name}) ) : [];

    const node_lines = nodes_str.split('\n')
    node_lines.slice(1).forEach((line, index) => {
      // const [id_way, node_id, cross_ways] = line.split(',\\');
      const id_way = line.split(',"')[0];
      if(id_way){
        nodes[index] = {
          lat: 0,
          lon: 0,
          way_id: Number(id_way),
          name: names.find(n => n.id == id_way)?.name
        }
      }
    })

    const edge_lines = edges_str.split('\n')
    edge_lines.slice(1).forEach((line, index) => {
      const [source_way,target_way] = line.split(',');
      if(source_way){
        edges[index] = {
          from: source_way,
          to: target_way,
          id: index.toString(),
        }
      }
    })

    this.LgraphData = {
      nodes: nodes,
      edges: edges
    }
  }
}
