import { Component, OnInit, ViewChild, AfterViewInit, ElementRef, OnDestroy, Input, ChangeDetectorRef } from '@angular/core';
import { FileService } from '../services/file.service';
import { FormControl } from '@angular/forms';
import {density, diameter, simpleSize} from 'graphology-metrics/graph';
import { tap, zip } from 'rxjs';
import Sigma from "sigma";
import Graph from 'graphology';
import iwanthue from "iwanthue";
import forceAtlas2 from 'graphology-layout-forceatlas2';
import circular from "graphology-layout/circular";
import {AbstractGraph} from 'graphology-types';
import saveAs from './saveAsPNG';
import { GraphData, GraphDataSrvice } from '../services/graph-data.service';

var graphml = require('graphology-graphml/browser');
var Graphology = require('graphology');

@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.css']
})
export class GraphComponent implements OnInit, AfterViewInit {
  @ViewChild('sigmaContainer') container!: ElementRef;
  @Input() name?: string;

  @Input() graphData?: GraphData;

  metrics?: {density: number, diameter: number, simpleSize: number};

  graph!: AbstractGraph;
  renderer?: Sigma;
  palette: string[] = [];
  labelsThreshold = new FormControl<number>(0);

  constructor(
    private cdRef: ChangeDetectorRef,
    private gdService: GraphDataSrvice,
    private fileService: FileService,
  ) {
    // this.graph = Graph.from(data as SerializedGraph);
    // this.graph = Graph.from(smallGraph as SerializedGraph);
    // this.palette = iwanthue(smallGraph.nodes.length, { seed: "eurSISCountryClusters" });
  }

  ngOnInit(): void {
  }

  ngAfterViewInit(): void {
    this.fileService.readFile('/assets/graphs/MurinoLO-4_graphml (1).graphml').subscribe(res => {
      this.graph = graphml.parse(Graphology, res);
      this.setAttributes();
      this.render();
      this.getMetrics();
    });
    // this.graph = new Graph();
    // if(!this.graphData) return;

    // const inters = this.gdService.streetsToIntersections(this.graphData);


    // inters.nodes.forEach(node => this.graph.addNode(node.node_id, {x: Number(node.lat), y: Number(node.lon), size: 5}));
    // inters.edges.forEach(edge => this.graph.addEdge(edge.from, edge.to, {label: edge.street_name, size: 5}));

    // this.getMetrics();

    // this.render();
  }

  getMetrics(){
    this.metrics = {
      density: density(this.graph),
      diameter: diameter(this.graph),
      simpleSize: simpleSize(this.graph)
    }
    this.cdRef.detectChanges();
  }

  setAttributes(){
    const nodes = this.graph.nodes();

    this.palette = iwanthue(this.graph.nodes().length, { seed: "eurSISCountryClusters" });

    this.graph.nodes().forEach((node, i) => {
      const angle = (i * 2 * Math.PI) / this.graph.order;
      this.graph.setNodeAttribute(node, "x", nodes.length * Math.cos(angle));
      this.graph.setNodeAttribute(node, "y", nodes.length * Math.sin(angle));
      
      // const size = Math.sqrt(this.graph.degree(node)) / 2;
      const size = this.graph.degree(node) / nodes.length * 100;
      this.graph.setNodeAttribute(node, "size", size > 5 ? size : 5);

      this.graph.setNodeAttribute(node, "color", this.palette.pop());

      const label = this.graph.getNodeAttribute(node, 'name');
      this.graph.setNodeAttribute(node, "label", label);
    });

    this.graph.forEachEdge((edge, attrs: any) => {
      attrs.size = 3;
    })
    
  }
  
  render(){
    if(!this.graph) return;

    // const degrees = this.graph.nodes().map((node) => this.graph.degree(node));
    // const minDegree = Math.min(...degrees);
    // const maxDegree = Math.max(...degrees);
    // const minSize = 2, maxSize = 10;
    // this.graph.forEachNode((node) => {
    //   const degree = this.graph.degree(node);
    //   this.graph.setNodeAttribute(
    //     node,
    //     "size",
    //     minSize +((degree - minDegree) / (maxDegree - minDegree)) * (maxSize - minSize)
    //   );
    // });

    circular.assign(this.graph);
    forceAtlas2.assign(this.graph, { settings: forceAtlas2.inferSettings(this.graph),  iterations: 600 });
    // this.forceLayout = new ForceSupervisor(this.graph, {settings: {repulsion: 1, inertia: 0.3}});
    // this.forceLayout = new FA2Layout(graph, {settings: forceAtlas2.inferSettings(this.graph)});
    // this.forceLayout?.start();


    this.renderer = new Sigma(this.graph as any, this.container.nativeElement,  {renderEdgeLabels: true, renderLabels: true});
    
    this.labelsThreshold.valueChanges.subscribe(val => {
      this.renderer?.setSetting("labelRenderedSizeThreshold", + (val ? val : 0));
    })

    const labelsThreshold = this.renderer.getSetting("labelRenderedSizeThreshold");
    if(labelsThreshold) this.labelsThreshold.setValue( labelsThreshold );
  }


  onSaveAs(type: 'png' | 'svg'){
    if(!this.renderer) return;

    const layers = ["edges", "nodes", "labels"];  
    saveAs( type, this.renderer, layers);
  }
}
