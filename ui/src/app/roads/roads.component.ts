import { ChangeDetectorRef, Component, Input, OnInit } from '@angular/core';
import * as L from 'leaflet';
import { SearchService } from '../services/search.service';
var osmtogeojson = require('osmtogeojson');
import 'leaflet-easyprint';

@Component({
  selector: 'app-roads',
  templateUrl: './roads.component.html',
  styleUrls: ['./roads.component.css']
})
export class RoadsComponent implements OnInit {
  private _bounds?: L.LatLngBounds;
  @Input() set bounds(val: L.LatLngBounds | undefined){
    this._bounds = val;
    if(val && this.map) this.updateRoads(this.map, val);
  };
  get bounds(){ return this._bounds };

  loading: boolean = false;
  printControl: any;
  gds?: L.GeoJSON;
  map?: L.Map;
  options: L.MapOptions = {
    layers: [

    ] as L.Layer[],
  };
  constructor(
    private searchService: SearchService,
    private cdRef: ChangeDetectorRef
  ) { }

  ngOnInit(): void {
  }

  onMapReady(map: L.Map){
    this.map = map;
    this.setTools(map);
    if(this.bounds){
      this.updateRoads(map, this.bounds)
    }
  }

  updateRoads(map: L.Map, bounds: L.LatLngBounds){
    this.loading = true;
    this.gds?.clearLayers();
    this.searchService.getRoadsOsm({
      s: bounds.getSouth(),
      w: bounds.getWest(),
      n: bounds.getNorth(),
      e: bounds.getEast()
    }).subscribe((res: any) => {
      this.loading = false;
      this.cdRef.detectChanges();
      this.gds = L.geoJSON(osmtogeojson(res)).addTo(map);
      map.fitBounds(this.gds.getBounds());
      map.setMaxBounds(map.getBounds());
      map.setMinZoom(map.getZoom());
      this.gds.setStyle({
        color: 'black'
      })
    })
  }

  setTools(map: L.Map){
    this.printControl = (L as any).easyPrint({
      title: 'Print Me',
      position: 'bottomleft',
      sizeModes: ['Current'],
      filename: 'export.png',
      exportOnly: true,
      tileWait: 4000,
      hidden: true,
      hideControlContainer: true
    }).addTo(map);

    const exportMap = ExportMap(() => this.printControl.printMap('CurrentSize'));
    new exportMap().addTo(map);
  }

}

export const ExportMap = (mainFn: (ev: any) => void) => L.Control.extend({
  options: {
		position: 'topleft',
		clearText: '<span class="material-symbols-outlined" style="line-height: inherit;">save_alt</span>',
		clearTitle: 'Export as .png',
	},
  onAdd(map: L.Map) {
		const polymodename = 'leaflet-control-export', container = L.DomUtil.create('div', `${polymodename} leaflet-bar`), options = this.options;
		this._clearButton = this._createButton(map, options.clearText, options.clearTitle, `${polymodename}`, container, mainFn);
		return container;
	},
  _clearButton: document.createElement('a'),
	_createButton(map: L.Map, html: string, title: string, className: string, container: HTMLElement, fn: (ev: any) => void) {
		const link = L.DomUtil.create('a', className, container);
		link.innerHTML = html;
		link.href = '#';
		link.title = title;
		link.setAttribute('role', 'button');
		link.setAttribute('aria-label', title);
		L.DomEvent.disableClickPropagation(link);
		L.DomEvent.on(link, 'click', L.DomEvent.stop);
		L.DomEvent.on(link, 'click', fn, this);
		L.DomEvent.on(link, 'click', ((ev: any) => {
      if(ev && ev.screenX > 0 && ev.screenY > 0){
        map.getContainer().focus();
      }
    }));
		return link;
	},
});
