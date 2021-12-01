/* eslint-disable @typescript-eslint/no-explicit-any*/

import React, {createContext, useContext} from 'react';

declare global {
    interface Window {
      CUCUMBER_MESSAGES:any;
    }
}

const initialState = {gherkin: null};

export const GlobalContext = createContext(initialState);

export const GlobalProvider = (props: { children: any; gherkin: any; }) : JSX.Element => {
    const { children, gherkin } = props;
    
    initialState.gherkin = gherkin;

    return (
        <GlobalContext.Provider
        value={{gherkin}}
        >
            {children}
        </GlobalContext.Provider>
    )
}

export function useGlobalContext() : any {
    return useContext(GlobalContext);
}