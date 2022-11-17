import { Component, OnInit, ViewChild, AfterViewInit, ElementRef, OnDestroy, Input, ChangeDetectorRef } from '@angular/core';
import {AbstractGraph } from "graphology-types";
import Sigma from "sigma";
import iwanthue from "iwanthue";
import { FileService } from '../services/file.service';
import { FormControl } from '@angular/forms';
import ForceSupervisor from "graphology-layout-force/worker";
import forceAtlas2 from 'graphology-layout-forceatlas2';
import FA2Layout from 'graphology-layout-forceatlas2/worker';
import {density, diameter, simpleSize} from 'graphology-metrics/graph';
import saveAsPNG from './saveAsPNG';

var graphml = require('graphology-graphml/browser');
var Graphology = require('graphology');

@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.css']
})
export class GraphComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('sigmaContainer') container!: ElementRef;
  @Input() name?: string;

  metrics?: {
    density: number, diameter: number, simpleSize: number
  };

  graph!: AbstractGraph;
  renderer?: Sigma;
  palette: string[] = [];

  forceLayout?: ForceSupervisor;

  labelsThreshold = new FormControl<number>(0);

  constructor(
    private fileService: FileService,
    private cdRef: ChangeDetectorRef
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
  }

  ngOnDestroy(): void {
    this.forceLayout?.kill();
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
    // initiate sigma
    this.renderer = new Sigma(this.graph, this.container.nativeElement);
  
    // this.forceLayout = new ForceSupervisor(this.graph, {settings: {repulsion: 1, inertia: 0.3}});
    this.forceLayout = new FA2Layout(this.graph, {settings: forceAtlas2.inferSettings(this.graph)});
    this.forceLayout?.start();

    this.labelsThreshold.valueChanges.subscribe(val => {
      if(this.renderer)
      this.renderer.setSetting("labelRenderedSizeThreshold", + (val ? val : 0));
    })

    const labelsThreshold = this.renderer.getSetting("labelRenderedSizeThreshold");
    if(labelsThreshold) this.labelsThreshold.setValue( labelsThreshold );
  }

  onSaveAsPng(){
    if(!this.renderer) return;
    const layers = ["edges", "nodes", "labels"];  
    saveAsPNG(this.renderer, layers);
  }

}