import React from 'react';
import './Modal.css';

interface ModalProps{
    children: React.ReactNode;
    title: string;
    onClose: () => void;
}

export function Modal({children, title, onClose}: ModalProps) {
    return (
        <>
            <div className="backModal" onClick={onClose}></div>
            <div className="frontModal">
                <h1 className="modal-text">{title}</h1>
                {children}
            </div>

        </>
    )
}