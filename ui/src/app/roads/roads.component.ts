import { ChangeDetectorRef, Component, Input, OnInit } from '@angular/core';
import { SearchService } from '../services/search.service';
import { GraphData } from '../services/graph-data.service';
import iwanthue from 'iwanthue';
import { saveText } from '../graph/saveAsPNG';
import * as L from 'leaflet';
import 'leaflet-easyprint';

@Component({
  selector: 'app-roads',
  templateUrl: './roads.component.html',
  styleUrls: ['./roads.component.css']
})
export class RoadsComponent implements OnInit {
  markerIcon = L.divIcon({className: 'roadPoint'});
  private _gd: GraphData | undefined;
  @Input() set graphData(val: GraphData | undefined){
    this._gd = val;
    if(val) this.updateRoads(val);
  }
  get graphData(){ return this._gd }

  loading: boolean = false;
  printControl: any;
  // gds?: L.GeoJSON;

  roads = new L.FeatureGroup([]);

  map?: L.Map;
  options: L.MapOptions = {
    layers: [
      this.roads
    ] as L.Layer[],
    center: [55.754527, 37.619509],
    zoom: 10,
  };
  constructor(
  ) { }

  ngOnInit(): void {
  }

  onMapReady(map: L.Map){
    this.map = map;
    this.setTools(map);
    if(this.graphData) this.updateRoads(this.graphData);
  }

  updateRoads(gd: GraphData){
    if(!this.map) return;
    this.roads.clearLayers();

    gd.nodes.forEach(node => {
      L.marker([ Number(node.lat), Number(node.lon)], {icon: this.markerIcon}).addTo(this.roads);
    })

    const pallete = iwanthue(gd.edges.length, {seed: 'someFunnySeed'});
    gd.edges.forEach((edge, index) => {
      const fromNode = gd.nodes.find(n => n.node_id == edge.from);
      const toNode = gd.nodes.find(n => n.node_id == edge.to);
      if(!(fromNode && toNode)) return;

      L.polyline([
        [Number(fromNode.lat), Number(fromNode.lon)], 
        [Number(toNode.lat), Number(toNode.lon)]
      ], {color: pallete[index], weight: 7}).bindTooltip(edge.street_name).addTo(this.roads);
    })
    
    this.map.fitBounds(this.roads.getBounds());
  }

  setTools(map: L.Map){
    const exportMap = ExportMap(() => {
      saveText(
        'export.svg',
        (document.getElementsByClassName('leaflet-overlay-pane')[1].lastChild as any).outerHTML,
        'image/svg+xml'
      )
    });
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
