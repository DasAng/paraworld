/* eslint-disable @typescript-eslint/no-explicit-any*/
import React from 'react';
import Features from './Features';
import { Overview } from './Overview';


export const Home = () : JSX.Element => {

    return (
        <div>
            <Overview></Overview>
            <br></br>
            <Features></Features>
        </div>
    )
}