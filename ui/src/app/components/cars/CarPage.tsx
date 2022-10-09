import React, { useEffect, useState } from 'react';
import './Car.css';
import {Link, useParams} from "react-router-dom"
import { Api } from '../../../services/api.service';
import { Car } from '../../../interfaces/car' 
import { useNavigate, useLocation } from "react-router-dom";

function CarPage(props: {creating?: boolean}) {
  const api = new Api();
  const navigate = useNavigate();
  const [car, setCar] = useState<Car>();
  const [carToEdit, setCarToEdit] = useState<Car>();
  const [editing, setEditing] = useState<boolean>(false)

  const [numberDirty, setNumberDirty] = useState<boolean>(false)
  const [ownerDirty, setOwnerDirty] = useState<boolean>(false)
  const [odometerDirty, setOdometerDirty] = useState<boolean>(false)
  const [modelDirty, setModelDirty] = useState<boolean>(false)

  const [numberError, setNumberError] = useState("Number format: A999AA 99")
  const [ownerError, setOwnerError] = useState("Owner format (passport): 9999999999")
  const [odometerError, setOdometerError] = useState("Can't be empty")
  const [modelError, setModelError] = useState("Can't be empty and consists more than 30 symbols")

  const [formValid, setFormValid] = useState<boolean>(false)

  const search = useLocation().search;

  useEffect(() => {
    if(props.creating){
      setEditing(true)
      return
    }


    const ed = new URLSearchParams(search).get('editing');
    setEditing(!!ed)
  })

  let { id } = useParams();
  
  const getCar = (id: string) => {
    api.getCar(id).then(res => {
      setCar(res);
      setCarToEdit(res);
    }).catch(err => {
      alert(err);
      window.location.href = '/';
    });
  }

  useEffect(() => {
    if(props.creating){
      let newCar = {
        id: 0,
        car_number: '',
        odometer: 0,
        owner: 0,
        model: '',
        picture: ''
      }
      setCar(newCar)
      setCarToEdit(newCar)
      return
    }
  }, [])
  
  useEffect(() => {
    if(id) getCar(id)
  }, [id])

  function onDelete(id: number){
    api.deleteCar(id).then(res => {
      navigate('/');
    })
  }

  function onEdit(){
    setNumberError('')
    setOwnerError('')
    setOdometerError('')
    setModelError('')
    setFormValid(true)

    navigate('?editing=true');
    setEditing(true);
  }

  function onCancel(){
    navigate('');
    setEditing(false);
    setCarToEdit(car)
  }

  function handleSubmit(){
    if(carToEdit){
      if(props.creating){
        api.postCar(carToEdit).then(res => {
          navigate('/car/'+res.id);
        })
      } else {
        api.putCar(carToEdit).then(res => {
          setCar(res);
          setCarToEdit(res);
          navigate('');
          setEditing(false);
        })
      }
    }  
  }

  function handleChange(event: any, field: string){
    if(carToEdit) {
      setCarToEdit(
        {
          ...carToEdit, 
          [field]: (event.target as HTMLInputElement).value
        }
      );
    }
  }

  useEffect(() => {
    if (numberError || ownerError || odometerError || modelError) {
      setFormValid(false)
    }
    else {
      setFormValid(true)
    }
  }, [numberError, ownerError, odometerError, modelError])

  const numberHandler = (e: any, field: string) => {
    handleChange(e, field)
    if (!carNumberValid(e.target.value)) {
      setNumberError('Number format: A999AA 99')
    } 
    else { 
      setNumberError('')
    }
  }

  const ownerHandler = (e: any, field: string) => {
    handleChange(e, field)
    if (!ownerDataValid(e.target.value)) {
      setOwnerError('Owner format (passport): 9999999999')
    } 
    else {
      setOwnerError('')
    }
  }

  const odometerHandler = (e: any, field: string) => {
    handleChange(e, field)
    if (!odometerValid(e.target.value)) {
      setOdometerError("Can't be empty")
    } 
    else {
      setOdometerError('')
    }
  }

  const modelHandler = (e: any, field: string) => {
    handleChange(e, field)
    if (!carModelValid(e.target.value)) {
      setModelError("Can't be empty and consists more than 30 symbols")
    } 
    else {
      setModelError('')
    }
  }

  const blurHandler = (e: any) => {
    switch (e.target.name) {
      case 'number':
        setNumberDirty(true)
        break
      case 'model':
        setModelDirty(true)
        break
      case 'owner':
        setOwnerDirty(true)
        break
      case 'odometer':
        setOdometerDirty(true)
        break
    }
  }

  function onAddPucture(ev: any){
    const file = ev.target.files[0];

    const reader = new FileReader()
    reader.onloadend = () => {
      if(carToEdit)
        setCarToEdit({
        ...carToEdit,
        picture: reader.result ? reader.result.toString() : ''
      })
    }

    reader.readAsDataURL(file)
  }

  return (
    <>
  {car ?
    <>

    <div className="wrap-buttons">
          { !props.creating &&
            <div className="wrap-change-button" onClick={onEdit}>
                <div className="change-button">
                    <svg viewBox="0 0 32 32" width="32px" height="32px">
                        <path id="pen" fill="#333333" d="M29.395,2.58C27.75,0.937,25.584,0,23.449,0c-1.801,0-3.459,0.668-4.67,1.877l-4.867,4.904 c-0.015,0.014-0.032,0.023-0.047,0.038c-0.008,0.008-0.013,0.019-0.021,0.026l0.002,0.002L3.517,17.256 c-0.476,0.473-0.821,1.062-1.013,1.705l-2.349,8.508C0.153,27.492,0,28.16,0,28.5C0,30.432,1.569,32,3.504,32 c0.385,0,1.13-0.184,1.157-0.188l8.478-2.229c0.644-0.191,1.229-0.539,1.705-1.016l15.263-15.383 C32.883,10.406,32.57,5.75,29.395,2.58z M16.014,23.795c-0.082-0.902-0.337-1.787-0.719-2.627l9.455-9.454 c0.578,1.826,0.281,3.736-0.986,5.004c-0.008,0.008-0.018,0.013-0.025,0.021l0.014,0.013l-7.728,7.79 C16.025,24.293,16.037,24.049,16.014,23.795z M14.793,20.256c-0.373-0.613-0.797-1.205-1.322-1.729 c-0.611-0.611-1.312-1.09-2.044-1.492l9.532-9.532c0.748,0.332,1.465,0.805,2.098,1.438c0.541,0.539,0.959,1.143,1.281,1.771 L14.793,20.256z M10.486,16.562c-0.926-0.373-1.896-0.586-2.868-0.599l7.703-7.762c1.179-1.15,2.896-1.481,4.587-1.062 L10.486,16.562z M4.167,29.873C4.058,29.898,3.719,29.984,3.489,30C2.667,29.99,2,29.322,2,28.5 c0.012-0.168,0.079-0.457,0.102-0.562l1.053-3.814c1.143-0.031,2.373,0.414,3.34,1.383c0.982,0.98,1.444,2.234,1.394,3.391 L4.167,29.873z M8.874,28.637c-0.024-1.342-0.57-2.738-1.672-3.838C6.16,23.756,4.796,23.154,3.436,23.1l0.996-3.607 c0.072-0.24,0.215-0.477,0.391-0.684c2.006-1.436,5.091-1.012,7.234,1.133c2.267,2.266,2.617,5.586,0.871,7.568 c-0.116,0.061-0.233,0.119-0.359,0.156L8.874,28.637z M28.691,11.772l-1.684,1.697c0-0.226,0.027-0.443,0.006-0.674 c-0.176-1.935-1.078-3.806-2.543-5.269c-1.629-1.63-3.789-2.565-5.928-2.571l1.656-1.67C21.027,2.458,22.184,2,23.449,2 c1.609,0,3.262,0.728,4.533,1.995c1.193,1.191,1.904,2.671,2.006,4.168C30.082,9.56,29.621,10.841,28.691,11.772z"/>
                    </svg>
                </div>
            </div>
          }
            <Link to="/"  style={{textDecoration: 'none', color: 'black'}}><div className="submit-back">To List Cars</div></Link>
          {
            !props.creating && 
            <div className="wrap-delete-button" onClick={() => onDelete(car.id)}>
                <div className="delete-button">
                    <svg x="0px" y="0px" width="32px" height="32px" viewBox="0 0 32 32" enable-background="new 0 0 32 32">
                        <path fill-rule="evenodd" clip-rule="evenodd" fill="#333333" stroke-width="1" d="M29.98,6.819c-0.096-1.57-1.387-2.816-2.98-2.816h-3v-1V3.001 c0-1.657-1.344-3-3-3H11c-1.657,0-3,1.343-3,3v0.001v1H5c-1.595,0-2.885,1.246-2.981,2.816H2v1.183v1c0,1.104,0.896,2,2,2l0,0v17 c0,2.209,1.791,4,4,4h16c2.209,0,4-1.791,4-4v-17l0,0c1.104,0,2-0.896,2-2v-1V6.819H29.98z M10,3.002c0-0.553,0.447-1,1-1h10 c0.553,0,1,0.447,1,1v1H10V3.002z M26,28.002c0,1.102-0.898,2-2,2H8c-1.103,0-2-0.898-2-2v-17h20V28.002z M28,8.001v1H4v-1V7.002 c0-0.553,0.447-1,1-1h22c0.553,0,1,0.447,1,1V8.001z"/>
                    </svg>
                </div>
            </div>
          }
        </div>
        
      
    </>
    :
    <div>Loading...</div>
}
      { car && carToEdit &&
        <>
              <form onSubmit={(ev) => {
                ev.preventDefault();
                handleSubmit();
              }} >
                <div className="wrap-car-info"> 
                <div className="first-info">
                <div className="info-field">
                    <input value={carToEdit.car_number} onBlur={e => blurHandler(e)} placeholder='Number' name="number" type="text" 
                    className="input-text" disabled={!editing} onChange={(ev) => numberHandler(ev, 'car_number')}/>
                    {(numberDirty && numberError) && <div className="error-handler" style={{color:'red'}}>{numberError}</div>}
                </div>
                
                <div className="info-field">
                    <input value={carToEdit.model} onBlur={e => blurHandler(e)} placeholder='Model' name="model" type="text" 
                    className="input-text" disabled={!editing} onChange={(ev) => modelHandler(ev, 'model')}/>
                    {(modelDirty && modelError) && <div className="error-handler" style={{color:'red'}}>{modelError}</div>}
                </div>
                </div>
                <div className="second-info">
                <div className="info-field">
                    <input value={carToEdit.owner} onBlur={e => blurHandler(e)} placeholder='Owner' name="owner" type="text" 
                    className="input-text" disabled={!editing} onChange={(ev) => ownerHandler(ev, 'owner')}/>
                    {(ownerDirty && ownerError) && <div className="error-handler" style={{color:'red'}}>{ownerError}</div>}
                </div>
                
                <div className="info-field">
                    <input value={carToEdit.odometer} onBlur={e => blurHandler(e)} placeholder='Odometr' name="odometer" type="text" 
                    className="input-text" disabled={!editing} onChange={(ev) => odometerHandler(ev, 'odometer')}/>
                    {(odometerDirty && odometerError) && <div className="error-handler" style={{color:'red'}}>{odometerError}</div>}
                </div>
              </div>
              </div>
        <label>
          <div className="wrap-submit-button">
            {/* <div className="submit-button" style={{cursor: editing ? 'pointer' : 'not-allowed'}}>Submit</div> */}
            <input className="create-button"  type="submit" value="Submit" disabled={!formValid}/>
          </div>
        </label>
        

          </form>
        </>
      }
    </>
  );
}

export default CarPage;


const ownerDataRE = new RegExp('^[0-9]{10}');
const odometerRE = new RegExp(`^[0-9]+[.]?[0-9]+$`);

const symbols = '[АВЕКМНОРСТУХавекмнорстухABEKMHOPCTYXabtkmnopctyx]'; 
const carNumberRE:RegExp[] = [new RegExp(`^${symbols}{1}[0-9]{3}${symbols}{2} [0-9]{2,3}$`), 
                              new RegExp(`^${symbols}{2}[0-9]{3} [0-9]{2,3}$`),
                              new RegExp(`^${symbols}{2}[0-9]{4} [0-9]{2,3}$`),
                              new RegExp(`^[0-9]{4}${symbols}{2} [0-9]{2,3}$`),
                              new RegExp(`^${symbols}{1}[0-9]{4} [0-9]{2,3}$`),
                              new RegExp(`^[0-9]{4}${symbols}{1} [0-9]{2,3}$`)];


function carNumberValid(str: string = "") {
    for (let i = 0; i <= 5; ++i) {
        if (carNumberRE[i].test(str)) { return true;}
    }
    return false
}


function carModelValid(str: string = "") {
    if (str.length > 0 && str.length < 30) { return true; }
    return false;
}


function ownerDataValid(str: string = "") {
    if (ownerDataRE.test(str)) { return true; }
    return false;
}


function odometerValid(str: string = "") {
    if (odometerRE.test(str)) { return true; }
    return false;

}