import React, {useContext, useEffect, useState} from 'react';
import './Car.css';
import { Car } from '../../../interfaces/car';
import { Link, useNavigate } from 'react-router-dom';
import { Api } from '../../../services/api.service';
import {CreateCar} from "../creation/CreateCar";
import {Modal} from "../Modal";
import {ModalContext} from "../../ModalContext/ModalContext";



function CarList() {
    const api = new Api(); 
    const navigate = useNavigate();
    const [cars, setCars] = useState<Car[]>([]);
    const [carDataSource, setCarDataSource] = useState<Car[]>([]);
    const [search, setSearch] = useState<string>('');
    const [scrolled, setScrolled] = useState<boolean>(false);
    const [page, setPage] = useState<number>(0);
    const [isFetching, setIsFetching] = useState(true);
    
    
    const getCars = () => {
        api.getCars(page).then(res => {
            if(!res.length) setScrolled(true);
            setCars(cars.concat(res))
            setPage(page + 1)
            
           }).finally(() => {
            setIsFetching(false);
           })

        
    }

    function onSearch(search: string){
        if(search.length){
            setCarDataSource(getSearch(search));
        } else {
            setCarDataSource([]);
        }
    }

    function getSearch(search: string){
        return cars.filter(car => {
            const s = search.toLocaleLowerCase();
            return car.odometer.toString().includes(s) ||
            car.model.toLocaleLowerCase().includes(s) ||
            car.car_number?.toString().includes(s) ||
            car.owner?.toString().includes(s)
        })
    }

    function onCreateCar(){
        navigate('/car/new')
    }

    
    function handleScroll() {
        if (window.innerHeight + document.documentElement.scrollTop < document.documentElement.offsetHeight) return;
        if(!scrolled)
            setIsFetching(true);
    }

    useEffect(() => {
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    useEffect(() => {
        if (!isFetching) return;
        getCars();
      }, [isFetching])


    return (
        <>
            <div className="search">
            <button onClick ={onCreateCar} className="create-button">Create Car Note</button>
            <div className="search-field">
                <input id='search' name='Search' type="text" className="input-text" placeholder="search car" onChange={(ev) => onSearch(ev.target.value)}/>
                <div className="wrap-search-button">
            <label htmlFor="Search">
                <div className="search-button"></div>
                </label>
            </div>
            </div>
            
            </div>
            { !!carDataSource.length &&
            <div className='cars-wrap search-result-wrap'>
                {carDataSource.map(car => 
                <Link to={'/car/' + car.id} className='carCard' key={'car-' + car.car_number} style={{textDecoration: 'none', color: 'black'}}>                
                    <div className='car'>                            
                            <div className="wrap-car-info"><div className="number main-info-car">{car.car_number}</div><div className="dop-info-car">number</div></div>
                            <div className="wrap-car-info"><div className="number main-info-car">{car.model}</div><div className="dop-info-car">model</div></div>
                            <div className="wrap-car-info"><div className="number main-info-car">{car.owner}</div><div className="dop-info-car">owner</div></div>
                            <div className="wrap-car-info"><div className="number main-info-car">{car.odometer}</div><div className="dop-info-car">odometer</div></div>
                    </div> 
                </Link>) 
                }                
                </div>
            }
            
            

            <div className='cars-wrap'>
                { cars.map(car => (
                <Link to={'/car/' + car.id} className='carCard' key={'car-' + car.car_number} style={{textDecoration: 'none', color: 'black'}}>                
                    <div className='car'>                            
                            <div className="wrap-car-info"><div className="number main-info-car">{car.car_number}</div><div className="dop-info-car">number</div></div>
                            <div className="wrap-car-info"><div className="number main-info-car">{car.model}</div><div className="dop-info-car">model</div></div>
                            <div className="wrap-car-info"><div className="number main-info-car">{car.owner}</div><div className="dop-info-car">owner</div></div>
                            <div className="wrap-car-info"><div className="number main-info-car">{car.odometer}</div><div className="dop-info-car">odometer</div></div>
                    </div> 
                </Link>))
                }                
            </div>

        
            <div id='bottom' 
            style={{width: '100%', height: '5px', marginBottom: "10px"}}>
            </div>

            {isFetching && !scrolled &&
                <div>Loading...</div>
            }

            {scrolled &&
                <div style={{textAlign: 'center', width: '100%', marginBottom: '30px'}}>
                    <span className='loadMore' onClick={() => {setScrolled(false); getCars(); }}>Try to load more cars</span>
                </div>
            }   

            {/* {modal && <Modal title="Create car information" onClose = {close}>
                <CreateCar onCreate={close} />
            </Modal>} */}
        </>
  );
}

function isInViewport(element: HTMLElement) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}


export default CarList;
