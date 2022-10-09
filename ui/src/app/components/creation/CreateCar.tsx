import React, {ChangeEvent, ReactEventHandler, ReactHTMLElement, useContext, useState} from 'react';
import './CreateCar.css';
//import axios from 'axios';
import {Car} from "../../../interfaces/car";
import {Api} from "../../../services/api.service";
import {ModalContext} from "../../ModalContext/ModalContext";

import { useParams } from "react-router-dom"
import {Modal} from "../Modal";

interface CreateCarProps {
    onCreate: () => void
}

export function CreateCar({onCreate}:CreateCarProps) {
    const api = new Api();
    const [car, setCar] = useState<Car>();
    const [carToCreate, setCarToCreate] = useState<Car>();
    const [creating, setCreating] = useState<boolean>(false);
    const {modal,open,close} = useContext(ModalContext);
    const [error, setError] = useState('');

    function handleChange(event: any, field: string){

        if(carToCreate)
            setCarToCreate(
                {
                    ...carToCreate,
                    [field]: (event.target as HTMLInputElement).value
                }
            );
    }

    function handleSubmit(event: React.FormEvent){
        //TODO here would be put request

        event.preventDefault()
        close();

        // if (value.trim().length === 0) {
        //     setError('Please enter valid data')
        // }

        setCar(carToCreate)
        setCreating(false);

        onCreate()
    }

    return(
        <form onSubmit={handleSubmit}>
            <label className="input-label">
                Number:
                <input type="text"
                    className = "create-input"
                    placeholder="Enter car number..."
                    value={carToCreate?.car_number}
                    onChange={(ev:ChangeEvent<HTMLInputElement>) => handleChange(ev,'number')}/>
            </label>
            <br/>
            <label className="input-label">
                Model:
                <input type="text"
                       className = "create-input"
                       placeholder="Enter car model..."
                value={carToCreate?.model}
                onChange={(ev:ChangeEvent<HTMLInputElement>) => handleChange(ev,'model')}/>
            </label>
            <br/>
            <label className="input-label">
                Owner:
                <input type="text"
                       className = "create-input"
                       placeholder="Enter car owner..."
                value={carToCreate?.owner}
                onChange={(ev:ChangeEvent<HTMLInputElement>) => handleChange(ev,'owner')}/>
            </label>
            <br/>
            <label className="input-label">
                Odometer:
                <input type="text"
                       className = "create-input"
                       placeholder="Enter car odometer..."
                       value={carToCreate?.model}
                       onChange={(ev:ChangeEvent<HTMLInputElement>) => handleChange(ev,'odometer')}/>
            </label>
            <br/>
            <button type="submit" className="edit-button" onClick={() => {setCreating(true); close();}}>Create</button>
            <button className="edit-button" onClick={() => {setCreating(false); close();}}>Cancel</button>
        </form>
    )
}