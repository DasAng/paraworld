/* eslint-disable @typescript-eslint/no-explicit-any*/

import React, {createContext, useContext} from 'react';

declare global {
    interface Window {
      CUCUMBER_MESSAGES:any;
      TEST_RESULT:any;
    }
}

const initialState = {gherkin: null, testResult: null};

export const GlobalContext = createContext(initialState);

export const GlobalProvider = (props: { children: any; gherkin: any; testResult: any}) : JSX.Element => {
    const { children, gherkin, testResult } = props;
    
    initialState.gherkin = gherkin;
    initialState.testResult = testResult;

    return (
        <GlobalContext.Provider
        value={{gherkin, testResult}}
        >
            {children}
        </GlobalContext.Provider>
    )
}

export function useGlobalContext() : any {
    return useContext(GlobalContext);
}