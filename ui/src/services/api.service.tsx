import { Car } from '../interfaces/car'

const serverUrl = 'http://localhost:8002';
export class Api {
    makeRequest<T>(options: {
        method: 'POST' | 'PUT' | "GET" | 'DELETE',
        endpoint: string,
        body?: any,
        options?: any
    }): Promise<T>{
        return fetch(options.endpoint,
             {...options.options, method: options.method, 
                body: options.body ?  JSON.stringify(options.body) : undefined, 
                headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
              },}
             
             ).then(res => res.json())
    }


    getCars(page: number = 0, per_page: number = 10): Promise<Car[]>{
        return this.makeRequest({
            endpoint:  `${serverUrl}/api/car?page=${page}&per_page=${per_page}`,
            method: 'GET',
        })
    }

    getCar(id: string | number): Promise<Car>{
        return this.makeRequest({
            endpoint:  `${serverUrl}/api/car/${id}/`,
            method: 'GET',
        })
    }

    postCar(car: Car): Promise<Car>{
        return this.makeRequest({
            endpoint:  `${serverUrl}/api/car/`,
            method: 'POST',
            body: car
        })
    }

    putCar(car: Car): Promise<Car>{
        return this.makeRequest({
            endpoint: `${serverUrl}/api/car/`,
            method: 'PUT',
            body: car
        })
    }

    deleteCar(id: number): Promise<{succsess: boolean}>{
        return this.makeRequest({
            endpoint:  `${serverUrl}/api/car/${id}`,
            method: 'DELETE',
        })
    }

}