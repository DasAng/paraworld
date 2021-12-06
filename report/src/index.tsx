import React from "react";
import ReactDOM from "react-dom";
import {GlobalProvider} from './GlobalContext';
import {Home} from './Home';

const App = () => (
  <GlobalProvider gherkin={window.CUCUMBER_MESSAGES} testResult={window.TEST_RESULT}>
     <Home></Home>
  </GlobalProvider>
);

ReactDOM.render(
  <App />,
  document.getElementById("root")
);