import React from 'react'

interface ErrorMentionProps {
    error:string;
}

export function ErrorMention({error}:ErrorMentionProps) {
    return(
        <p className="error-text" style={{color:"red", textAlign:"center"}}>{error}</p>
    )
}