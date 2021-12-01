/* eslint-disable @typescript-eslint/no-explicit-any*/
import React from 'react';
import Features from './Features';
import {useGlobalContext} from './GlobalContext';


export const Home = () : JSX.Element => {

    const {gherkin} = useGlobalContext();

    return (
        <div>
            <Features></Features>
        </div>
    )
}