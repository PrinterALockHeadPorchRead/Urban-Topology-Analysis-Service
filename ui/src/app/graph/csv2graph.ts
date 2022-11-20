import { Injectable } from '@angular/core';
import Graph from "graphology";

@Injectable({providedIn: 'root'})
export class Csv2Graph {
    // graph: Graph = new Graph();
    constructor() {
    }

    getNodesFromCsv(graph: Graph, csvString: string, params?: any){
        const lines = csvString.split('\n');
        lines.slice(1).forEach(line => { 
            const [id, lat, lon] = line.split(',');
            graph.addNode(id, {x: Number(lat), y: Number(lon), ...params});
        })
    }

    getEdgesFromCsv(graph: Graph, csvString: string, params?: any){
        const lines = csvString.split('\n');
        lines.slice(1).forEach(line => { 
            const [src, target, label] = line.split(',');
            graph.addEdge(src, target, {type: 'line', label: label, ...params});
        })
    }
}