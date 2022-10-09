import React from "react";
import './Toolbar.css'

function Toolbar(props: any){
    return(
        <p className='toolbar'>
            {props.children}
        </p>
    );
}
export default Toolbar;