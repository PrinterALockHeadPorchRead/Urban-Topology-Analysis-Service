import React, {useContext} from 'react';
import './App.css';
import Toolbar from './components/toolbar/Toolbar';
import CarList from './components/cars/CarList';
import {BrowserRouter as Router, Routes, Route, Link} from "react-router-dom";
import CarPage from './components/cars/CarPage';
import {Modal} from './components/Modal'
import {CreateCar} from "./components/creation/CreateCar";
import {ModalContext} from "./ModalContext/ModalContext";
import Creation from './components/cars/Creation';

function App() {

    return (
        <>
          <Router>

          <div className="wrap-header">
            <div className="logo">
                <div className="main-logo">Simple REST API</div>
                <div className="wrap-mini-logo">
                    <div className="top-logo">by Ingria team</div>
                    <div className="bottom-logo">for SberCorus</div>
                </div>
            </div>
          </div>
          <div>
            
          </div>

              <Routes>
                <Route path="/" element={<CarList></CarList>}></Route>
                <Route path="/car/new" element={<Creation></Creation>}></Route>
                <Route path="/car/:id" element={<CarPage></CarPage>}></Route>
              </Routes>

              <div className="svg-1">
            <svg height="300" width="500">
                <defs>
                    <linearGradient id="Gradient2" x1="0" x2="0" y1="0" y2="1">
                        <stop offset="0%" stop-color="#7532a8"/>
                        <stop offset="100%" stop-color="#a83297"/>
                      </linearGradient>
                </defs>
                <path d="M19,28 C115,13 213,70 500,200" stroke="white" stroke-width="0" fill="url(#Gradient2)" />
                <path d="M20,27 C27,109 164,110 500,200" stroke="white" stroke-width="0" fill="url(#Gradient2)" />
            </svg> 
         </div>

         <div className="svg-2">
         <svg height="300" width="500"> 
            <defs> 
            <linearGradient id="Gradient2" x1="0" x2="1" y1="0" y2="0"> 
            <stop offset="0%" stop-color="#a83297"/> 
            <stop offset="100%" stop-color="#8888ff"/> 
            </linearGradient> 
            </defs> 
            <path d="M2,164 C171,196 385,121 428,60 "  stroke-width="0" fill="url(#Gradient2)" /> 
            <path d="M3,165 C163,47 409,16 428,60 "  stroke-width="0" fill="url(#Gradient2)"  /> 
            </svg> 
         </div>

          </Router>

        </>
    );
}

export default App;
