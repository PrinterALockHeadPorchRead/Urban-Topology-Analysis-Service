import {ChangeDetectorRef, Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Region, Town, _distBounds, _districts } from '../interfaces/town';
import { FileService } from '../services/file.service';
import { TownService } from '../services/town.service';
import { GraphDataSrvice, GraphData, INode, Edge } from '../services/graph-data.service';

import * as L from 'leaflet'; //* - все
import { map, zip } from 'rxjs';

enum sections{
  map = 'map',
  graph = 'graph',
  roads = 'roads'
}


@Component({
  selector: 'app-town',
  templateUrl: './town.component.html',
  styleUrls: ['./town.component.css']
})
export class TownComponent implements OnInit{

  id?: string;
  town?: Town;
  graphData?: GraphData;
  graphName = '';
  roadBounds?: L.LatLngBounds;

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
        this.id=id;
        this.townService.getTown( id ).subscribe(
          town=>{
            this.town = town;
            // if(town.districtFolder) 
            this.getDistricts(town);
          },
          error=>{this.router.navigate(['/towns'])}
        )
      }
    })
  }

  ngOnInit(): void {}

  getCenter(): L.LatLngTuple{
    if(!this.town) return [59.9414, 30.3267];
    return [ this.town.property.center.latitude, this.town.property.center.longitude ];
  }

  getDistricts(town: Town): void{
    zip(
      ...[2, 1, 0].map(key => this.townService.getTownRegions(town.id, key))
    ).subscribe(res => town.districts = {0: res[0], 1: res[1], 2: res[2]})
    
  }

  handlePolygon(ev: {name: string, polygon: any}){
    this.graphName = ev.name;
    this.section = sections.graph;
    this.roadBounds = (ev.polygon as L.Polygon)?.getBounds();
    this.getGraphData();
  }
  
  getGraphData(){
    zip(
      this.fileService.readFile('/assets/graphs/nodes.csv').pipe(map(csvString => this.graphDataService.csv2object<INode>(csvString, ["node_id","lat","lon"]))),
      this.fileService.readFile('/assets/graphs/graph.csv').pipe(map(csvString => this.graphDataService.csv2object<Edge>(csvString, ["from","to","street_name"])))
    ).subscribe(values => {
      this.graphData = {nodes: values[0], edges: values[1]}
      this.cdRef.detectChanges(); // нужно для того, чтобы граф нормально отрисовался (без этого отрисовка происходит только после повтороного нажатия на карту)
    });
  }
}
