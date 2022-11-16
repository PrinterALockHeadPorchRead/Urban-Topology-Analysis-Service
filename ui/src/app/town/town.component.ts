import {ChangeDetectorRef, Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Region, Town, _distBounds, _districts } from '../interfaces/town';
import { FileService } from '../services/file.service';
import { TownService } from '../services/town.service';
import * as L from 'leaflet'; //* - все
import { GraphComponent } from '../graph/graph.component';
import { districtLevels } from '../interfaces/town';

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

  sidebarOpened: boolean = false;
  id?: string;
  town?: Town;
  graph = false;
  graphName = '';
  roadBounds?: L.LatLngBounds;

  private _section: sections = sections.map;
  set section(val: sections){
    this._section = val;
    const achor = document.getElementsByName(val)[0];
    achor?.scrollIntoView({behavior: 'smooth'});
  } get section(){return this._section}; // section=val вызывает set section(val), val=section вызывает get section

  constructor(
    private townService: TownService,
    private route: ActivatedRoute,
    private router: Router,
    private fileService: FileService,
    private cdRef: ChangeDetectorRef
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
    // Object.keys(districtLevels).map(filename => {
    //   this.fileService.readJson(`/assets/districts/${town.districtFolder}/${filename == 'city' ? town.districtFolder : filename}.json`).subscribe((res: any) => {
    //     const info = res as _distBounds;
    //     town.districts[filename as districtLevels] = info.features;
    //   })
    // })

    town.districts = {0: [], 1: [], 2: []};
    [2, 1, 0].forEach(key => this.townService.getTownRegions(town.id, key).subscribe(res => {
      town.districts[key as districtLevels] = res;
    }) )
    
  }

  // getFeatures(){
  //   if(!this.town) return { city: [], children: [], subchildren: [] };
  //   return {
  //     city: this.town.districts.city,
  //     children: this.town.districts.children,
  //     subchildren: this.town.districts.subchildren
  //   }
  // }

  handlePolygon(ev: {name: string, polygon: any}){
    this.graph = true;
    this.graphName = ev.name;
    this.section = sections.graph;
    this.roadBounds = (ev.polygon as L.Polygon)?.getBounds();
    this.cdRef.detectChanges(); // нужно для того, чтобы граф нормально отрисовался (без этого отрисовка происходит только после повтороного нажатия на карту)
  }

  goUp(){
    const secs = Object.keys(sections);
    const idx = secs.findIndex(s => s == this.section);
    if(idx == 0) return;
    this.section = secs[idx - 1] as sections;
    this.cdRef.detectChanges();
  }
  goDown(){
    const secs = Object.keys(sections);
    const idx = secs.findIndex(s => s == this.section);
    if(idx == secs.length-1) return;
    this.section = secs[idx + 1] as sections;
    this.cdRef.detectChanges();
  }
}
